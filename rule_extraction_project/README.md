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

- `data/interim/`：解析后的 JSON；含 **`{stem}_formula_blocks.json`**（公式块启发式定位，供后续 OCR/渲染分支）
- `data/processed/`：画像、分段计划、segments、**`*_extracted.json`**、**`*_constraints.json`**、**`*_consequences.json`**、**`*_normalized.json`**（含 **`parent_rule_id` 回填**、条款格式整理、类型轻量纠偏）
- **normalize 额外写出**：**`*_formulas.json`**、**`*_variables.json`**、**`*_constraints_enriched.json`**（约束行增加 **`formula_id`**，并与公式块/派生公式对齐）
- `outputs/tables/`：上述文件的 CSV 镜像；主表看 **`*_rules_normalized.csv`**，约束增强看 **`*_constraints_enriched.csv`**
- `data/eval/`：**`*_eval_report.json`**（规则层统计 + 子表层统计；有金标后可再扩展 F1）

## 测试

```bash
pytest
```
