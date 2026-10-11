from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents, chunk_size=500, chunk_overlap=50):
    """Splits loaded documents into smaller chunks for better retrieval."""
    
    if not documents:
        print("Warning: No documents to split.")
        return []

    print(f"Splitting {len(documents)} document(s)...")
    
    # Setup the splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Perform the split
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunk(s) from the documents.")
    
    return chunks