from src.utils.hashing import deterministic_review_id


def test_hashing_deterministic() -> None:
    a = deterministic_review_id("p", "u", "t", "r", "d")
    b = deterministic_review_id("p", "u", "t", "r", "d")
    assert a == b
