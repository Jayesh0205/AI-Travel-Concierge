
import requests
from ddgs import DDGS
from langchain.tools import tool

from rag.qa import answer_question


def create_tools(uploaded_text: str = ""):
    """Create NovaTrip tools scoped to the current request."""

    @tool
    def travel_knowledge_search(question: str) -> str:
        """Search the travel knowledge base and the current uploaded document."""
        try:
            return answer_question(
                question,
                uploaded_text=uploaded_text or None,
            )
        except Exception:
            return (
                "Travel knowledge search is temporarily unavailable. "
                "Please try again."
            )

    @tool
    def itinerary_planner(
        destination: str,
        duration_days: int,
        interests: str,
        budget: str,
    ) -> str:
        """Prepare instructions for a suggested day-by-day itinerary."""
        if not destination.strip():
            return "Please provide a destination."

        if not 1 <= duration_days <= 30:
            return "Trip duration must be between 1 and 30 days."

        interests = interests.strip() or (
            "popular attractions and local experiences"
        )
        budget = budget.strip() or "not specified"

        return (
            f"Create a {duration_days}-day itinerary for {destination}.\n"
            f"Traveler interests: {interests}.\n"
            f"Budget: {budget}.\n\n"
            "Use travel_knowledge_search or web_search when useful. "
            "Include practical tips. Do not invent confirmed prices, "
            "bookings, opening hours, or live availability."
        )

    @tool
    def web_search(query: str) -> str:
        """Search the web for current travel information and destination details."""
        if not query.strip():
            return "Please provide a search query."

        try:
            with DDGS() as search_client:
                results = search_client.text(
                    query,
                    max_results=5,
                )

            if not results:
                return "No web search results were found."

            lines = []
            for result in results:
                title = result.get("title", "Untitled")
                body = result.get("body", "")
                url = result.get("href", "")
                lines.append(
                    f"Title: {title}\n"
                    f"Summary: {body}\n"
                    f"URL: {url}"
                )

            return "\n\n".join(lines)

        except Exception:
            return (
                "Web search is temporarily unavailable. "
                "Check your internet connection and try again."
            )

    @tool
    def current_weather(city: str) -> str:
        """Get current weather conditions for a city using Open-Meteo."""
        if not city.strip():
            return "Please provide a city name."

        try:
            search_name = city.strip()
            requested_country = "india"

            # Allow inputs such as "Goa, India" or "Paris, France".
            if "," in search_name:
                parts = [part.strip() for part in search_name.split(",")]
                search_name = parts[0]
                requested_country = parts[-1].casefold()

            # Use known coordinates for Goa to avoid incorrect geocoding.
            if search_name.casefold() == "goa":
                location = {
                    "name": "Panaji",
                    "admin1": "Goa",
                    "country": "India",
                    "latitude": 15.4909,
                    "longitude": 73.8278,
                }
            else:
                geo_response = requests.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={
                        "name": search_name,
                        "count": 10,
                        "language": "en",
                        "format": "json",
                    },
                    timeout=10,
                )
                geo_response.raise_for_status()
                locations = geo_response.json().get("results", [])

                exact_matches = [
                    item for item in locations
                    if item.get("name", "").casefold()
                    == search_name.casefold()
                    and item.get("country", "").casefold()
                    == requested_country
                ]

                if not exact_matches:
                    return (
                        f"Could not confidently find '{search_name}' "
                        f"in {requested_country.title()}. "
                        "Please check the city name."
                    )

                location = exact_matches[0]


            latitude = location["latitude"]
            longitude = location["longitude"]

            weather_response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": (
                        "temperature_2m,relative_humidity_2m,"
                        "apparent_temperature,precipitation,"
                        "wind_speed_10m"
                    ),
                    "timezone": "auto",
                },
                timeout=10,
            )
            weather_response.raise_for_status()

            data = weather_response.json()
            current = data.get("current")

            if not current:
                return "Current weather data is unavailable."

            units = data.get("current_units", {})
            place = ", ".join(
                str(value)
                for value in (
                    location.get("name"),
                    location.get("admin1"),
                    location.get("country"),
                )
                if value
            )

            return (
                f"Current weather for {place}\n"
                f"Observed time: {current.get('time', 'Not provided')}\n"
                f"Temperature: {current.get('temperature_2m')} "
                f"{units.get('temperature_2m', '°C')}\n"
                f"Feels like: {current.get('apparent_temperature')} "
                f"{units.get('apparent_temperature', '°C')}\n"
                f"Relative humidity: {current.get('relative_humidity_2m')}%\n"
                f"Precipitation: {current.get('precipitation')} "
                f"{units.get('precipitation', 'mm')}\n"
                f"Wind speed: {current.get('wind_speed_10m')} "
                f"{units.get('wind_speed_10m', 'km/h')}\n"
                "Source: Open-Meteo"
            )

        except requests.RequestException:
            return (
                "Weather service is temporarily unavailable. "
                "Please try again later."
            )
        except (ValueError, KeyError, TypeError):
            return "The weather service returned an unexpected response."

    return [
        travel_knowledge_search,
        itinerary_planner,
        web_search,
        current_weather,
    ]
