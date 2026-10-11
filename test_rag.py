from rag.retriever import get_retriever
from rag.qa import get_rag_chain

print("--- FINAL LCEL RAG PIPELINE TEST ---")

# 1. Setup Retriever
retriever = get_retriever(k=2)

# 2. Setup QA Chain
rag_chain = get_rag_chain(retriever)

# 3. Ask a Question
question = "What are the popular beaches in South Goa?"
print(f"\nUser Question: {question}")
print("Thinking...\n")

# 4. Get the AI Answer directly
response = rag_chain.invoke(question)

print("--- NOVA-TRIP AI ANSWER ---")
print(response)