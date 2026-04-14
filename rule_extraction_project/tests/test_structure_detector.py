from src.parsers.structure_detector import detect_structure


def test_detect_article():
    text = "第一章 总则\n第一条 为了规范……\n第二条 本法所称……"
    hits = detect_structure(text)
    assert len(hits.articles) >= 2
