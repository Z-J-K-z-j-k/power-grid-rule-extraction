"""Centralized prompts for planner and extraction."""

EXTRACTION_SYSTEM = """你是电力监管/并网类法规结构化抽取助手。只输出合法 JSON，不要 Markdown 代码围栏。
从片段中抽取 0 条或多条「原子规则」。复杂条款要拆成多条（主规则、处罚、豁免、计算方式分开）。
严禁用 OTHER 作为 rule_category；若不确定，用最接近的具体类别（如 penalty_rule、exemption_rule、procedure）。
modality 表示规范强度：MUST / MUST_NOT / MAY / SHOULD / NOT_APPLICABLE（纯计算说明可用 NOT_APPLICABLE）。
rule_category 与 modality 不同：前者是规则类型，后者是义务强弱。
parent_rule_ref 填父规则条文定位（如「第十六条主规则」），无则空字符串。
每条可带 constraints（阈值/指标）与 consequences（处罚/上限），数组可为空。"""


def extraction_user_prompt(segment_text: str) -> str:
    return f"""片段如下（可能含多条「条/款/项」及公式、考核、免考）：

---
{segment_text}
---

请输出唯一 JSON 对象，格式为：
{{"rules": [
  {{
    "rule_category": "definition|scope|responsibility|obligation|prohibition|permission|procedure|threshold_rule|calculation_rule|penalty_rule|exemption_rule|special_case_rule|reporting_rule|testing_rule",
    "modality": "MUST|MUST_NOT|MAY|SHOULD|NOT_APPLICABLE",
    "rule_level": "primary|secondary|attached",
    "parent_rule_ref": "",
    "chapter": "",
    "section": "",
    "article": "",
    "clause": "",
    "item": "",
    "subject": "",
    "trigger_condition_text": "",
    "condition": "",
    "action": "",
    "object": "",
    "time_limit": "",
    "location_or_scope": "",
    "exception": "",
    "consequence": "",
    "metric": "",
    "comparator": "",
    "threshold": "",
    "unit": "",
    "consequence_formula": "",
    "cap": "",
    "basis_text": "",
    "constraints": [
      {{
        "constraint_type": "threshold|range|tolerance|timing|capacity_requirement|formula_input|prerequisite",
        "metric_name": "",
        "comparator": "",
        "threshold_value": "",
        "unit": "",
        "qualifier_text": "",
        "time_window_text": "",
        "region_special_case_text": "",
        "formula_text": "",
        "notes": ""
      }}
    ],
    "consequences": [
      {{
        "consequence_type": "penalty|penalty_cap|no_compensation|refund|exemption|reward|administrative_requirement",
        "penalty_mode": "",
        "trigger_text": "",
        "value_text": "",
        "formula_text": "",
        "cap_text": "",
        "unit": "",
        "notes": ""
      }}
    ]
  }}
]}}

basis_text 必须填支撑该条规则的最短原文引用。无信息则填空字符串；数组可省略或为空数组。"""


PLANNER_SYSTEM = """你是文档分段策略助手。根据文档画像输出 JSON：primary_unit, merge_short, min_chars, extra_rules (字符串数组), rationale。"""


def planner_user_prompt(profile_summary: str) -> str:
    return f"""文档画像摘要：
{profile_summary}

请给出适合法规类 PDF 的分段策略 JSON。"""
