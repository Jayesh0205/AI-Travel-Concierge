import os
from langchain_chroma import Chroma
from rag.embeddings import get_embeddings_model

def create_or_get_vector_store(chunks, persist_directory="chroma_db"):
    """Creates a Chroma vector database from document chunks."""
    
    if not chunks:
        print("Error: No chunks provided to create the vector store.")
        return None
        
    print(f"Initializing Vector Store at '{persist_directory}'...")
    
    # Get the Gemini embedding model
    embeddings = get_embeddings_model()
    
    # Create the Chroma database and save it locally
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("Vector database created successfully.")
    return vectorstore