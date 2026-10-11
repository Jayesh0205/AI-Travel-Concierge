
from langchain_chroma import Chroma

from rag.embeddings import get_embeddings
from rag.vectorstore import create_vectorstore


COLLECTION_NAME = "novatrip_travel"


def get_retriever():
    """Return a retriever with an initialized travel knowledge base."""

    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory="chroma_db",
        embedding_function=embeddings,
    )

    # Check whether the collection contains any records.
    existing_records = vectorstore.get(limit=1)

    # Build the knowledge base only when the collection is empty.
    if not existing_records.get("ids"):
        vectorstore = create_vectorstore()

    return vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )
