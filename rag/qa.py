from rag.retriever import get_retriever
from agent.llm import get_llm


def answer_question(question):

    retriever = get_retriever()

    documents = retriever.invoke(question)

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = f"""
You are NovaTrip, an AI travel assistant.

Answer the user's question using the travel information provided below.

Travel Information:
{context}

User Question:
{question}

Instructions:
- Use the provided travel information.
- Give a clear and helpful answer.
- Do not invent facts that are not supported by the provided information.
- If the information is not available, say that the knowledge base does not contain enough information.
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    if isinstance(response.content, list):

        text_response = ""

        for item in response.content:

            if isinstance(item, dict) and item.get("type") == "text":
                text_response += item.get("text", "")

        return text_response

    return response.content
