from src.config.schemas import ExtractedRule
from src.normalizers.field_normalizer import normalize_rule_fields


def test_modal_inference():
    r = ExtractedRule(
        rule_id="r1",
        segment_id="s1",
        rule_type="",
        action="不得泄露国家秘密",
    )
    out = normalize_rule_fields(r)
    assert out.rule_type == "MUST_NOT"
