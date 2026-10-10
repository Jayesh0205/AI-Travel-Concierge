from rag.vectorstore import create_vectorstore


vectorstore = create_vectorstore()


print("Vector database created successfully!")

print("Documents stored:", vectorstore._collection.count())