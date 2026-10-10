from pathlib import Path


def load_documents():
    documents = []

    documents_path = Path("data/travel_documents")

    for file_path in documents_path.glob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append({
            "source": file_path.name,
            "content": text
        })

    return documents