from src.config.schemas import SegmentationPlan
from src.segmenters.hybrid_segmenter import hybrid_segment


def test_segment_merges_short():
    text = "第一条 内容较短\n\n第二条 这是第二条的内容，应该比第一条长很多，用于测试合并逻辑。"
    plan = SegmentationPlan(primary_unit="article", merge_short=True, min_chars=200)
    segs = hybrid_segment(text, plan)
    assert len(segs) >= 1
