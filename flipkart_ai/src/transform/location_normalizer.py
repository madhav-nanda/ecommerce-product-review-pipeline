"""Location parser for fields like 'Certified Buyer, Mumbai'."""


def parse_location(location_raw: str) -> tuple[str | None, str | None]:
    if not location_raw:
        return None, None
    parts = [p.strip() for p in location_raw.split(",")]
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]
