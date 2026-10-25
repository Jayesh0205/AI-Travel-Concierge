import os
import requests
from dotenv import load_dotenv

load_dotenv()

IGNAV_API_URL = "https://ignav.com/api"


def search_flights(origin, destination, departure_date):
    api_key = os.getenv("IGNAV_API_KEY")

    if not api_key:
        return {"error": "IGNAV_API_KEY is missing from .env"}

    try:
        response = requests.post(
            f"{IGNAV_API_URL}/fares/one-way",
            headers={
                "X-Api-Key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "market": "IN",
            },
            timeout=30,
        )

        if not response.ok:
            return {"error": f"Flight API returned HTTP {response.status_code}"}

        return response.json()

    except requests.RequestException:
        return {"error": "Could not connect to the flight API."}
