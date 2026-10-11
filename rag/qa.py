import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def format_docs(docs):
    """Formats the retrieved chunks into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain(retriever):
    """Creates a modern LCEL RAG chain."""
    print("Initializing Gemini LLM (LCEL Mode)...")
    
    # Perfectly indented line
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.3)

    system_prompt = (
        "You are a helpful travel assistant for NovaTrip. "
        "Use the following pieces of retrieved context to answer the user's question. "
        "If the answer is not in the context, just say you don't know. "
        "Keep the answer concise and friendly.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain