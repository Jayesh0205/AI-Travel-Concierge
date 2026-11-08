from types import SimpleNamespace
from unittest.mock import patch

from agent.workflow import run_travel_workflow
from database.pg_models import SavedSearch


class MockResearchTool:
    def __init__(self, name, response):
        self.name = name
        self.response = response
        self.calls = []

    def invoke(self, arguments):
        self.calls.append(arguments)
        return self.response


class FakeSession:
    records = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def add(self, record):
        self.records.append(record)

    def commit(self):
        pass


class FakeLLM:
    def invoke(self, prompt):
        return SimpleNamespace(
            content="Mock NovaTrip itinerary for Goa."
        )


def test_complete_travel_workflow():
    FakeSession.records = []

    tools = [
        MockResearchTool("travel_knowledge_search", "Mock RAG result"),
        MockResearchTool("web_search", "Mock web result"),
        MockResearchTool("current_weather", "Mock weather result"),
        MockResearchTool("flight_search", "Mock flight result"),
    ]

    def mock_tool_logging(tool, arguments, provider, endpoint):
        return {
            "result": tool.invoke(arguments),
            "success": True,
            "response_time_ms": 10,
            "error": None,
        }

    with patch("agent.workflow.create_tools", return_value=tools):
        with patch(
            "agent.workflow.call_tool_with_logging",
            side_effect=mock_tool_logging,
        ):
            with patch("agent.workflow.get_llm", return_value=FakeLLM()):
                with patch(
                    "agent.workflow.SessionLocal",
                    FakeSession,
                ):
                    result = run_travel_workflow(
                        user_request="Plan a 3-day Goa trip",
                        origin="BOM",
                        destination="GOI",
                        departure_date="2026-12-15",
                    )

    assert result == "Mock NovaTrip itinerary for Goa."

    assert all(len(tool.calls) == 1 for tool in tools)

    assert len(FakeSession.records) == 1

    saved_record = FakeSession.records[0]

    assert isinstance(saved_record, SavedSearch)
    assert saved_record.query == "Plan a 3-day Goa trip"
    assert saved_record.response == result

def test_empty_travel_request_returns_message():
    result = run_travel_workflow(user_request="")

    assert result == "Please enter a travel request."


def test_gemini_failure_propagates():
    tools = [
        MockResearchTool("travel_knowledge_search", "Mock RAG result"),
        MockResearchTool("web_search", "Mock web result"),
        MockResearchTool("current_weather", "Mock weather result"),
        MockResearchTool("flight_search", "Mock flight result"),
    ]

    def mock_tool_logging(tool, arguments, provider, endpoint):
        return {
            "result": tool.invoke(arguments),
            "success": True,
            "response_time_ms": 10,
            "error": None,
        }

    class FailingLLM:
        def invoke(self, prompt):
            raise RuntimeError("Mock Gemini failure")

    with patch("agent.workflow.create_tools", return_value=tools):
        with patch(
            "agent.workflow.call_tool_with_logging",
            side_effect=mock_tool_logging,
        ):
            with patch(
                "agent.workflow.get_llm",
                return_value=FailingLLM(),
            ):
                with patch(
                    "agent.workflow.SessionLocal",
                    FakeSession,
                ):
                    try:
                        run_travel_workflow(
                            user_request="Plan a Goa trip",
                            destination="Goa",
                        )
                    except RuntimeError as exc:
                        assert "Mock Gemini failure" in str(exc)
                    else:
                        assert False, "Expected Gemini failure to propagate"


def test_postgres_save_failure_does_not_stop_itinerary():
    class FailingSession(FakeSession):
        def commit(self):
            raise RuntimeError("Mock PostgreSQL failure")

    tools = [
        MockResearchTool("travel_knowledge_search", "Mock RAG result"),
        MockResearchTool("web_search", "Mock web result"),
        MockResearchTool("current_weather", "Mock weather result"),
        MockResearchTool("flight_search", "Mock flight result"),
    ]

    def mock_tool_logging(tool, arguments, provider, endpoint):
        return {
            "result": tool.invoke(arguments),
            "success": True,
            "response_time_ms": 10,
            "error": None,
        }

    with patch("agent.workflow.create_tools", return_value=tools):
        with patch(
            "agent.workflow.call_tool_with_logging",
            side_effect=mock_tool_logging,
        ):
            with patch(
                "agent.workflow.get_llm",
                return_value=FakeLLM(),
            ):
                with patch(
                    "agent.workflow.SessionLocal",
                    FailingSession,
                ):
                    result = run_travel_workflow(
                        user_request="Plan a Goa trip",
                        destination="Goa",
                    )

    assert result == "Mock NovaTrip itinerary for Goa."

