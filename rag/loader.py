from pathlib import Path


def load_documents():
    """Load non-empty TXT files from the travel knowledge folder."""

    documents_path = Path("data/travel_documents")

    if not documents_path.is_dir():
        raise FileNotFoundError(
            f"Travel documents folder not found: {documents_path.resolve()}"
        )

    documents = []

    for file_path in sorted(documents_path.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if text:
            documents.append({
                "source": file_path.name,
                "content": text
            })

    if not documents:
        raise ValueError(
            "No non-empty TXT files found in data/travel_documents. "
            "Add at least one travel knowledge document."
        )

    return documents