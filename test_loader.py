from rag.loader import load_documents


documents = load_documents()


print(f"Documents loaded: {len(documents)}")


for document in documents:

    print("\nSource:", document["source"])

    print("Characters:", len(document["content"]))
