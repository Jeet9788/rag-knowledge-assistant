import math

from app.retrieval import _sigmoid


def test_sigmoid_maps_logits_into_unit_range():
    # Cross-encoder logits are unbounded and frequently negative; every one of
    # them has to come back as a probability the UI can render.
    for logit in (-11.16, -3.0, 0.0, 2.5, 9.0):
        assert 0.0 <= _sigmoid(logit) <= 1.0


def test_sigmoid_is_monotonic_so_ordering_survives():
    logits = [-8.0, -1.5, 0.0, 0.5, 4.2]
    scores = [_sigmoid(x) for x in logits]
    assert scores == sorted(scores)


def test_sigmoid_centres_on_a_half():
    assert _sigmoid(0.0) == 0.5


def test_sigmoid_survives_extreme_logits():
    # math.exp(-x) overflows for x below about -745; the negative branch exists
    # so these return 0.0/1.0 instead of raising.
    assert _sigmoid(-1000.0) == 0.0
    assert math.isclose(_sigmoid(1000.0), 1.0)
