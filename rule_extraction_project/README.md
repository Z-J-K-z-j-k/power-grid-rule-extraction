# Rule extraction (法规规则抽取)

流水线：`parse → profile → plan → segment → extract → normalize → evaluate`。

## 配置

复制 `.env.example` 为 `.env`，填入 `DEEPSEEK_API_KEY` 等。

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
cd rule_extraction_project
python -m src.main --pdf data/raw/target_file.pdf --run all
```

`extract` 会对**每个 segment 各请求一次 API**；默认 **`EXTRACT_MAX_WORKERS=2`** 并行、**`API_MAX_RETRIES=6`** 对断连 / `incomplete chunked read` / 429 / 502 等做退避重试。仍不稳定时可在 `.env` 设 **`EXTRACT_MAX_WORKERS=1`** 串行。

若运行 `python -m src.main` 时**几乎没有任何输出**，请更新到当前代码：入口脚本在 `-m` 模式下 `__name__` 为 `__main__`，旧版曾因此未把日志接到已配置的 logger 上。

若只想先验证解析与分段，可只跑到 `segment`：

```bash
python -m src.main --pdf data/raw/target_file.pdf --run segment
```

分步：

```bash
python -m src.main --pdf data/raw/target_file.pdf --run parse
python -m src.main --pdf data/raw/target_file.pdf --run profile
python -m src.main --pdf data/raw/target_file.pdf --run plan
python -m src.main --pdf data/raw/target_file.pdf --run segment
python -m src.main --pdf data/raw/target_file.pdf --run extract
python -m src.main --pdf data/raw/target_file.pdf --run normalize
python -m src.main --pdf data/raw/target_file.pdf --run evaluate
```

## 输出

- `data/interim/`：解析后的 JSON
- `data/processed/`：画像、分段计划、segments、抽取与归一化结果
- `outputs/tables/`：CSV 导出
- `data/eval/`：评估占位报告

## 测试

```bash
pytest
```
