from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.loader import load_documents


def split_documents():

    documents = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = []

    for document in documents:

        document_chunks = splitter.create_documents(
            [document["content"]],
            metadatas=[
                {
                    "source": document["source"]
                }
            ]
        )

        chunks.extend(document_chunks)

    return chunks