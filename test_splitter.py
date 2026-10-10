from rag.splitter import split_documents


chunks = split_documents()


print(f"Total chunks: {len(chunks)}")


for i, chunk in enumerate(chunks):

    print("\n--- Chunk", i + 1, "---")

    print("Source:", chunk.metadata["source"])

    print("Characters:", len(chunk.page_content))

    print(chunk.page_content[:150])