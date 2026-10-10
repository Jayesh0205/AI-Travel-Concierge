from rag.embeddings import get_embeddings


embeddings = get_embeddings()


text = "Popular beaches in South Goa"


vector = embeddings.embed_query(text)


print("Embedding created successfully!")

print("Vector dimensions:", len(vector))

print("First 10 values:")

print(vector[:10])