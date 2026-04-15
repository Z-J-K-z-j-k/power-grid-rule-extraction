from src.config.schemas import ExtractedRule
from src.normalizers.citation_normalizer import normalize_citation_fields
from src.normalizers.parent_rule_linker import link_parent_rules


def test_parent_link_same_segment():
    rules = [
        ExtractedRule(
            rule_id="a",
            segment_id="s1",
            rule_level="primary",
            rule_category="obligation",
            basis_text="x",
        ),
        ExtractedRule(
            rule_id="b",
            segment_id="s1",
            rule_category="penalty_rule",
            basis_text="y",
        ),
    ]
    out = link_parent_rules(rules)
    assert out[1].parent_rule_id == "a"


def test_article_normalize_arabic():
    r = ExtractedRule(
        rule_id="r",
        segment_id="s",
        article="第 13 条",
        basis_text="",
    )
    out = normalize_citation_fields(r)
    assert "13" in out.article
