
from langchain_chroma import Chroma

from rag.embeddings import get_embeddings


COLLECTION_NAME = "novatrip_travel"


def get_retriever():

    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever