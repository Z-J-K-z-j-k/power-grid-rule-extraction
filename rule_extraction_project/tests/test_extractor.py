from src.config.schemas import ExtractedRule


def test_extracted_rule_schema():
    r = ExtractedRule(rule_id="r1", segment_id="s1", rule_type="MUST", action="测试")
    assert r.segment_id == "s1"
