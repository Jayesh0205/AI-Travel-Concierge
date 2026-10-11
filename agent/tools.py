
from langchain.tools import tool

from rag.qa import answer_question


# Stores the current uploaded document for this app session's request.
_uploaded_document = ""


def set_uploaded_document(text: str) -> None:
    """Set the optional document supplied through the Streamlit UI."""
    global _uploaded_document
    _uploaded_document = text


@tool
def travel_knowledge_search(question: str) -> str:
    """Search travel knowledge and any uploaded text document.

    Use for destination information, attractions, travel tips,
    and relevant information from a user's uploaded document.
    """
    return answer_question(
        question,
        uploaded_text=_uploaded_document or None,
    )


@tool
def itinerary_planner(
    destination: str,
    duration_days: int,
    interests: str,
    budget: str,
) -> str:
    """Prepare instructions for a suggested day-by-day itinerary.

    Args:
        destination: Destination for the trip.
        duration_days: Number of days, from 1 to 30.
        interests: Preferred activities or attractions.
        budget: Total budget or budget category.
    """
    if not destination.strip():
        return "Please provide a destination."

    if not 1 <= duration_days <= 30:
        return "Trip duration must be between 1 and 30 days."

    if not interests.strip():
        interests = "popular attractions and local experiences"

    if not budget.strip():
        budget = "not specified"

    return (
        f"Create a {duration_days}-day itinerary for {destination}.\n"
        f"Traveler interests: {interests}.\n"
        f"Budget: {budget}.\n\n"
        "Use travel_knowledge_search to find relevant information "
        "when appropriate. Organize the itinerary by day and include "
        "practical tips. Do not invent confirmed prices, bookings, "
        "opening hours, or live availability."
    )


TOOLS = [
    travel_knowledge_search,
    itinerary_planner,
]