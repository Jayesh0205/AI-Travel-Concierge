import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader

def load_travel_documents(data_dir="data/travel_documents"):
    """Loads all text documents from the specified directory."""
    
    # Check if directory exists to avoid crashes
    if not os.path.exists(data_dir):
        print(f"Error: The directory '{data_dir}' does not exist.")
        return []
    
    print(f"Loading documents from {data_dir}...")
    
    # DirectoryLoader reads all .txt files in the folder using TextLoader
    loader = DirectoryLoader(data_dir, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    print(f"Successfully loaded {len(documents)} document(s).")
    return documents