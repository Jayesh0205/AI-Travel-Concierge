
import time
from datetime import datetime
from typing import Any, TypedDict

from langgraph.graph import StateGraph, START, END

from agent.llm import get_llm
from agent.tools import create_tools
from database.pg_database import SessionLocal
from database.pg_models import SavedSearch, APIActivity


class TravelState(TypedDict):
    user_request: str
    uploaded_text: str
    origin: str
    destination: str
    departure_date: str
    research: dict[str, Any]
    itinerary: str
    errors: list[str]


def analyze_request(state: TravelState):
    """Validate the request and prepare research state."""

    if not state["user_request"].strip():
        return {
            "errors": ["Please enter a travel request."]
        }

    return {
        "research": {},
        "errors": [],
    }


def call_tool_with_logging(tool, arguments, provider, endpoint):
    """Run a tool and record its execution details."""

    started = time.perf_counter()
    success = False
    error_message = None
    result = ""

    try:
        result = tool.invoke(arguments)

        # Tools may return an error message instead of raising an exception.
        if isinstance(result, str) and (
            "temporarily unavailable" in result.casefold()
            or "could not connect" in result.casefold()
            or "returned http" in result.casefold()
            or " is missing from .env" in result.casefold()
        ):
            error_message = result
        else:
            success = True

    except Exception as exc:
        error_message = str(exc)
        result = f"{provider} research is unavailable."

    elapsed_ms = int((time.perf_counter() - started) * 1000)

    try:
        with SessionLocal() as session:
            activity = APIActivity(
                provider=provider,
                endpoint=endpoint,
                status_code=None,
                success=success,
                response_time_ms=elapsed_ms,
                error_message=error_message,
            )
            session.add(activity)
            session.commit()

    except Exception as exc:
        # Logging failure should not destroy the travel response.
        print(f"API activity logging failed: {exc}")

    return {
        "result": result,
        "success": success,
        "response_time_ms": elapsed_ms,
        "error": error_message,
    }


def research_travel(state: TravelState):
    """Collect travel knowledge, web, weather and optional flight data."""

    tools = {
        item.name: item
        for item in create_tools(state.get("uploaded_text", ""))
    }

    request = state["user_request"]
    research = {}

    # 1. Travel knowledge / RAG
    knowledge = call_tool_with_logging(
        tools["travel_knowledge_search"],
        {"question": request},
        "RAG",
        "travel_knowledge_search",
    )
    research["knowledge"] = knowledge["result"]

    # 2. Destination web research
    web = call_tool_with_logging(
        tools["web_search"],
        {
            "query": (
                request
                + " travel attractions and practical information"
            )
        },
        "DuckDuckGo",
        "web_search",
    )
    research["web"] = web["result"]

    # 3. Current weather, when a destination is known
    destination = state.get("destination", "").strip()

    if destination:
        weather = call_tool_with_logging(
            tools["current_weather"],
            {"city": destination},
            "Open-Meteo",
            "current_weather",
        )
        research["weather"] = weather["result"]
    else:
        research["weather"] = (
            "Weather search skipped: destination not provided."
        )

    # 4. Flight search only when all details are available
    origin = state.get("origin", "").strip().upper()
    departure_date = state.get("departure_date", "").strip()

    if origin and destination and departure_date:
        try:
            datetime.strptime(departure_date, "%Y-%m-%d")

            flight = call_tool_with_logging(
                tools["flight_search"],
                {
                    "origin": origin,
                    "destination": destination.upper(),
                    "departure_date": departure_date,
                },
                "IGNAV",
                "fares/one-way",
            )

            research["flights"] = flight["result"]

        except ValueError:
            research["flights"] = (
                "Flight search skipped: use departure date YYYY-MM-DD."
            )
    else:
        research["flights"] = (
            "Flight search skipped: provide origin, destination "
            "and departure date."
        )

    return {"research": research}



def generate_itinerary(state: TravelState):
    """Generate the final travel response using Gemini."""

    llm = get_llm()

    prompt = f"""
You are NovaTrip, an AI-powered travel concierge.

USER REQUEST:
{state['user_request']}

RESEARCH RESULTS:
{state.get('research', {})}

UPLOADED DOCUMENT:
{state.get('uploaded_text', '')}

INSTRUCTIONS:
1. Create a clear and useful travel response.
2. Organize itineraries day by day when appropriate.
3. Use the retrieved research where relevant.
4. Do not invent live prices, flight availability or bookings.
5. Clearly mention when weather or flight data was unavailable.
6. Distinguish retrieved information from your suggestions.
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, str):
        itinerary = content

    elif isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))

        itinerary = "\n\n".join(
            part for part in text_parts if part
        )

    else:
        itinerary = str(content)

    return {"itinerary": itinerary}

def save_trip(state: TravelState):
    """Save the generated travel response in PostgreSQL."""

    try:
        with SessionLocal() as session:
            record = SavedSearch(
                query=state["user_request"],
                response=state["itinerary"],
            )
            session.add(record)
            session.commit()

    except Exception as exc:
        print(f"PostgreSQL saved-search operation failed: {exc}")

    return {}

def build_travel_graph():
    """Build and compile the NovaTrip travel workflow."""

    graph = StateGraph(TravelState)

    graph.add_node("analyze", analyze_request)
    graph.add_node("research", research_travel)
    graph.add_node("generate", generate_itinerary)
    graph.add_node("save", save_trip)

    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "research")
    graph.add_edge("research", "generate")
    graph.add_edge("generate", "save")
    graph.add_edge("save", END)

    return graph.compile()




def run_travel_workflow(
    user_request: str,
    uploaded_text: str = "",
    origin: str = "",
    destination: str = "",
    departure_date: str = "",
) -> str:
    """Run the complete NovaTrip workflow."""

    if not user_request.strip():
        return "Please enter a travel request."

    workflow = build_travel_graph()

    initial_state: TravelState = {
        "user_request": user_request,
        "uploaded_text": uploaded_text,
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "research": {},
        "itinerary": "",
        "errors": [],
    }

    result = workflow.invoke(initial_state)

    return result["itinerary"]
