from rag.retriever import get_retriever


retriever = get_retriever()


query = "What are popular places in South Goa?"


results = retriever.invoke(query)


print("Query:", query)

print("\nRetrieved chunks:", len(results))


for i, document in enumerate(results):

    print("\n--- Result", i + 1, "---")

    print("Source:", document.metadata["source"])

    print(document.page_content)