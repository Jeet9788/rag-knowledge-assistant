from app.retrieval import _reciprocal_rank_fusion


def test_rrf_rewards_items_ranked_high_in_both_lists():
    vector = ["a", "b", "c"]
    keyword = ["b", "a", "d"]
    scores = _reciprocal_rank_fusion([vector, keyword])
    # 'a' and 'b' appear in both lists and should outrank single-list items
    assert scores["b"] > scores["c"]
    assert scores["a"] > scores["d"]


def test_rrf_handles_empty_lists():
    assert _reciprocal_rank_fusion([[], []]) == {}
