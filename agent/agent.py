
from langchain.agents import create_agent

from agent.llm import get_llm
from agent.prompts import SYSTEM_PROMPT
from agent.tools import create_tools


def create_novatrip_agent(uploaded_text: str = ""):
    """Create an agent with tools scoped to this request."""

    return create_agent(
        model=get_llm(),
        tools=create_tools(uploaded_text),
        system_prompt=SYSTEM_PROMPT,
    )


def run_agent(user_message: str, uploaded_text: str = "") -> str:
    """Run the agent using only this request's uploaded document."""

    if not user_message.strip():
        return "Please enter a travel question."

    agent = create_novatrip_agent(uploaded_text)

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