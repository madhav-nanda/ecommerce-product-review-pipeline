from src.transform.cleaner import clean_review_text


def test_cleaner_removes_read_more() -> None:
    out = clean_review_text("Great phone READ MORE")
    assert "read more" not in out
