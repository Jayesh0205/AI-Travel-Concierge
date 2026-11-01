
from unittest.mock import patch

from agent.workflow import call_tool_with_logging
from database.pg_database import SessionLocal
from database.pg_models import APIActivity


class FakeTool:
    def invoke(self, arguments):
        return "Mock travel research result"


def test_api_activity_logging():
    with patch("agent.workflow.SessionLocal", SessionLocal):
        result = call_tool_with_logging(
            FakeTool(),
            {"query": "Goa attractions"},
            "TEST_PROVIDER",
            "test_endpoint",
        )

    assert result["success"] is True
    assert result["result"] == "Mock travel research result"

    with SessionLocal() as session:
        record = (
            session.query(APIActivity)
            .filter_by(provider="TEST_PROVIDER")
            .order_by(APIActivity.id.desc())
            .first()
        )

        assert record is not None
        assert record.success is True
        assert record.response_time_ms is not None


def test_tool_error_is_logged():
    class FailingTool:
        def invoke(self, arguments):
            raise RuntimeError("Mock API failure")

    result = call_tool_with_logging(
        FailingTool(),
        {},
        "TEST_FAILURE",
        "test_endpoint",
    )

    assert result["success"] is False
    assert "Mock API failure" in result["error"]

from agent.workflow import research_travel


class MockResearchTool:
    def __init__(self, name, response):
        self.name = name
        self.response = response
        self.calls = []

    def invoke(self, arguments):
        self.calls.append(arguments)
        return self.response


def test_research_skips_flight_without_details():
    tools = [
        MockResearchTool("travel_knowledge_search", "Mock RAG result"),
        MockResearchTool("web_search", "Mock web result"),
        MockResearchTool("current_weather", "Mock weather result"),
        MockResearchTool("flight_search", "Mock flight result"),
    ]

    with patch("agent.workflow.create_tools", return_value=tools):
        with patch("agent.workflow.call_tool_with_logging") as mock_call:
            mock_call.side_effect = lambda tool, arguments, provider, endpoint: {
                "result": tool.invoke(arguments),
                "success": True,
                "response_time_ms": 10,
                "error": None,
            }

            result = research_travel({
                "user_request": "Plan a Goa trip",
                "uploaded_text": "",
                "origin": "",
                "destination": "Goa",
                "departure_date": "",
                "research": {},
                "itinerary": "",
                "errors": [],
            })

    assert "Mock RAG result" == result["research"]["knowledge"]
    assert "Mock web result" == result["research"]["web"]
    assert "Mock weather result" == result["research"]["weather"]
    assert "skipped" in result["research"]["flights"].lower()

    assert len(tools[0].calls) == 1
    assert len(tools[1].calls) == 1
    assert len(tools[2].calls) == 1
    assert len(tools[3].calls) == 0


def test_research_runs_flight_when_details_are_complete():
    tools = [
        MockResearchTool("travel_knowledge_search", "Mock RAG result"),
        MockResearchTool("web_search", "Mock web result"),
        MockResearchTool("current_weather", "Mock weather result"),
        MockResearchTool("flight_search", "Mock flight result"),
    ]

    with patch("agent.workflow.create_tools", return_value=tools):
        with patch("agent.workflow.call_tool_with_logging") as mock_call:
            mock_call.side_effect = lambda tool, arguments, provider, endpoint: {
                "result": tool.invoke(arguments),
                "success": True,
                "response_time_ms": 10,
                "error": None,
            }

            result = research_travel({
                "user_request": "Plan a Goa trip",
                "uploaded_text": "",
                "origin": "BOM",
                "destination": "GOI",
                "departure_date": "2026-12-15",
                "research": {},
                "itinerary": "",
                "errors": [],
            })

    assert result["research"]["flights"] == "Mock flight result"
    assert len(tools[3].calls) == 1
    assert tools[3].calls[0] == {
        "origin": "BOM",
        "destination": "GOI",
        "departure_date": "2026-12-15",
    }
