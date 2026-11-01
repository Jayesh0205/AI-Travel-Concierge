
"""Convert common city names into IATA airport codes."""

AIRPORT_CODES = {
    "mumbai": "BOM",
    "delhi": "DEL",
    "goa": "GOI",
    "dabolim": "GOI",
    "mopa": "GOX",
    "pune": "PNQ",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "kolkata": "CCU",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "kochi": "COK",
}


def normalize_airport_code(value: str) -> str:
    """Accept a known city name or an existing three-letter airport code."""
    value = value.strip().upper()

    # Check known city names first.
    if value.casefold() in AIRPORT_CODES:
        return AIRPORT_CODES[value.casefold()]

    # Otherwise, accept an existing three-letter airport code.
    if len(value) == 3 and value.isalpha():
        return value

    raise ValueError(
        f"Unknown airport or city: {value}. "
        "Please enter a supported city name or IATA code."
    )
