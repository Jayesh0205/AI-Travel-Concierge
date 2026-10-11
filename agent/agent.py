
from langchain.agents import create_agent

from agent.llm import get_llm
from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOLS


def create_novatrip_agent():
    """Create NovaTrip's AI agent with its registered tools."""

    return create_agent(
        model=get_llm(),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )


def run_agent(user_message: str) -> str:
    """Run the agent and return its final text response."""

    if not user_message.strip():
        return "Please enter a travel question."

    agent = create_novatrip_agent()

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_message}
        ]
    })

    # Find the last assistant message that isn't a tool call.
    for message in reversed(result["messages"]):
        if getattr(message, "type", "") != "ai":
            continue

        if getattr(message, "tool_calls", None):
            continue

        content = message.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = [
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            ]
            return "\n".join(part for part in text_parts if part)

    return "Sorry, I couldn't generate a final response. Please try again."