"""Centralized prompts for planner and extraction."""

EXTRACTION_SYSTEM = """你是法规/规章文本结构化抽取助手。只输出合法 JSON，不要 Markdown 代码围栏。
从给定片段中抽取 0 条或多条“规则”。每条规则对应 schema 中的字段；无信息则填空字符串。
rule_type 使用英文枚举：MUST, MUST_NOT, MAY, SHOULD, DEFINITION, OTHER。"""


def extraction_user_prompt(segment_text: str) -> str:
    return f"""片段如下（可能含多条“条/款/项”）：

---
{segment_text}
---

请输出 JSON 对象，格式严格为：
{{"rules": [{{"rule_type":"","subject":"","condition":"","action":"","object":"","time_limit":"","location_or_scope":"","exception":"","consequence":"","basis_text":""}}]}}

basis_text 填支撑该规则的原句或最短连续引用。"""


PLANNER_SYSTEM = """你是文档分段策略助手。根据文档画像输出 JSON：primary_unit, merge_short, min_chars, extra_rules (字符串数组), rationale。"""


def planner_user_prompt(profile_summary: str) -> str:
    return f"""文档画像摘要：
{profile_summary}

请给出适合法规类 PDF 的分段策略 JSON。"""
