from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv


load_dotenv()


def get_embeddings():

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    return embeddings