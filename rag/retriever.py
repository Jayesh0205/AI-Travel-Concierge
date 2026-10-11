from langchain_chroma import Chroma
from rag.embeddings import get_embeddings_model

def get_retriever(persist_directory="chroma_db", k=2):
    """Creates a retriever to fetch relevant chunks from ChromaDB."""
    
    print("Connecting to Vector Database for retrieval...")
    embeddings = get_embeddings_model()
    
    # Load the existing database
    vectorstore = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embeddings
    )
    
    # Create a retriever that returns the top 'k' most relevant chunks
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever