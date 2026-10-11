# ✈️ NovaTrip — AI Travel Concierge

NovaTrip is an AI-powered travel assistant built with Python, Streamlit, LangChain, and Google Gemini. It helps users explore destinations, access travel knowledge, and generate suggested itineraries.

## Features

* AI-powered travel planning and itinerary suggestions.
* Retrieval-Augmented Generation (RAG) over a travel knowledge base.
* Upload `.txt` documents to provide additional context.
* Tool-based agent architecture using LangChain.
* Streamlit web interface.
* Environment-variable-based API key configuration.
* Graceful handling of Gemini API quota errors.

## Technology Stack

* **Language:** Python
* **Frontend:** Streamlit
* **Agent framework:** LangChain
* **LLM:** Google Gemini
* **Knowledge retrieval:** ChromaDB and LangChain
* **Embeddings:** Google Gemini embeddings
* **Configuration:** python-dotenv

## Project Structure

```text
AI-Travel-Concierge/
├── agent/
│   ├── agent.py
│   ├── llm.py
│   ├── prompts.py
│   └── tools.py
├── data/
│   └── travel_documents/
│       ├── goa.txt
│       └── travel_tips.txt
├── rag/
│   ├── embeddings.py
│   ├── loader.py
│   ├── qa.py
│   ├── retriever.py
│   ├── splitter.py
│   └── vectorstore.py
├── app.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Install Python and Git.

2. Clone the repository:

   ```bash
   git clone https://github.com/Jayesh0205/AI-Travel-Concierge.git
   cd AI-Travel-Concierge
   ```

3. Create and activate a virtual environment on Windows:

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```cmd
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root and add your own Google Gemini API key:

   ```text
   GOOGLE_API_KEY=your_api_key_here
   ```

   Never commit your actual API key.

6. Start the application:

   ```cmd
   streamlit run app.py
   ```

## How It Works

1. The user enters a travel request in the Streamlit interface.
2. The agent selects its available tools when appropriate.
3. The RAG pipeline retrieves relevant information from the travel knowledge base.
4. An optional uploaded text document can provide additional context to the knowledge-search tool.
5. Google Gemini generates the response.

## Links

* **GitHub repository:** https://github.com/Jayesh0205/AI-Travel-Concierge
* **Live application:** https://novatrip.streamlit.app

## Limitations

* AI responses depend on Google Gemini availability and API quotas.
* Uploaded-document support currently accepts `.txt` files.
* The application does not confirm live flight prices, hotel availability, or bookings.

## Future Improvements

* Add live travel API integrations.
* Improve document retrieval and upload formats.
* Add database-backed search history.
* Improve itinerary export and user experience.
* Expand automated testing and error monitoring.
