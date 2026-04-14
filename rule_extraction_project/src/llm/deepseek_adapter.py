"""DeepSeek OpenAI-compatible chat completions."""

from __future__ import annotations

import random
import time

import httpx

from ..config.settings import (
    API_MAX_RETRIES,
    API_RETRY_BASE_SECONDS,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
)
from ..utils.logger import get_logger
from .client import LLMClient

log = get_logger("rule_extraction.llm")


class _RetryableHTTP(Exception):
    def __init__(self, status_code: int, snippet: str) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {snippet}")


# Transient network / server drops mid-body (e.g. incomplete chunked read)
_RETRYABLE_TRANSPORT = (
    httpx.RemoteProtocolError,
    httpx.ReadTimeout,
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.PoolTimeout,
)
if hasattr(httpx, "WriteError"):
    _RETRYABLE_TRANSPORT = _RETRYABLE_TRANSPORT + (httpx.WriteError,)


class DeepSeekAdapter(LLMClient):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else DEEPSEEK_API_KEY
        self.base_url = (base_url or DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or DEEPSEEK_MODEL

    def complete(self, system: str, user: str, *, temperature: float = 0.2) -> str:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # Fresh TCP connection per request — reduces flaky keep-alive / chunked EOF issues
            "Connection": "close",
        }
        timeout = httpx.Timeout(connect=60.0, read=600.0, write=60.0, pool=60.0)
        max_retries = API_MAX_RETRIES
        base_delay = API_RETRY_BASE_SECONDS

        last_err: BaseException | None = None
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=timeout) as client:
                    r = client.post(url, json=payload, headers=headers)
                    if r.status_code in (429, 502, 503, 504):
                        raise _RetryableHTTP(r.status_code, r.text[:300])
                    try:
                        r.raise_for_status()
                    except httpx.HTTPStatusError as e:
                        detail = ""
                        try:
                            detail = r.text[:500]
                        except Exception:
                            pass
                        raise RuntimeError(
                            f"DeepSeek HTTP {r.status_code} at {url}. Body (truncated): {detail}"
                        ) from e
                    data = r.json()
                return data["choices"][0]["message"]["content"]
            except _RETRYABLE_TRANSPORT as e:
                last_err = e
                if attempt >= max_retries - 1:
                    break
                delay = base_delay * (2**attempt) + random.uniform(0, 0.8)
                log.warning(
                    "DeepSeek transport error (%s): %s — retry %d/%d in %.1fs",
                    type(e).__name__,
                    e,
                    attempt + 2,
                    max_retries,
                    delay,
                )
                time.sleep(delay)
            except _RetryableHTTP as e:
                last_err = e
                if attempt >= max_retries - 1:
                    break
                delay = base_delay * (2**attempt) + random.uniform(0, 0.8)
                log.warning(
                    "DeepSeek HTTP %s — retry %d/%d in %.1fs",
                    e.status_code,
                    attempt + 2,
                    max_retries,
                    delay,
                )
                time.sleep(delay)

        assert last_err is not None
        raise RuntimeError(
            f"DeepSeek request failed after {max_retries} attempts: {last_err}"
        ) from last_err
