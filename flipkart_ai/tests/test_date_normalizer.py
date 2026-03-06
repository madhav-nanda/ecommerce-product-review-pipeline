from src.transform.date_normalizer import parse_relative_date


def test_parse_days_ago() -> None:
    dt = parse_relative_date("14 days ago", "2024-08-20T00:00:00+00:00")
    assert dt is not None
    assert dt.day == 6
