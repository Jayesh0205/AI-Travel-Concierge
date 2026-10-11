import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load API key from .env file
load_dotenv()

def get_embeddings_model():
    """Returns the Google Gemini embeddings model."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in the .env file.")
    
    print("Initializing Gemini Embeddings Model...")
    # Updated to the EXACT model name supported by your API key
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return embeddings