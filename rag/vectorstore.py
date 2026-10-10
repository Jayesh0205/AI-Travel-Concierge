
from langchain_chroma import Chroma

from rag.embeddings import get_embeddings
from rag.splitter import split_documents


COLLECTION_NAME = "novatrip_travel"


def create_vectorstore():

    chunks = split_documents()
    embeddings = get_embeddings()

    # Give every chunk a stable ID so reruns update
    # existing records instead of creating duplicates.
    ids = [
        f"{chunk.metadata.get('source', 'document')}-{index}"
        for index, chunk in enumerate(chunks)
    ]

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=ids,
        collection_name=COLLECTION_NAME,
        persist_directory="chroma_db"
    )

    return vectorstore