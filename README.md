# NovaTrip — AI Travel Concierge ✈️

NovaTrip is an AI-powered travel assistant built with Python, Streamlit, LangChain, and Google Gemini. It helps users explore destinations, retrieve travel information, generate suggested itineraries, check weather, search the web, and find flight options.

## 🌟 Features

- **AI Travel Assistant:** Responds to travel-related questions using Google Gemini.
- **Smart Itinerary Planning:** Generates suggested travel plans based on user requests.
- **Travel Knowledge Search (RAG):** Retrieves relevant information from a travel knowledge base.
- **Document Upload:** Supports `.txt` documents to provide additional travel context.
- **Flight Search:** Retrieves flight options through the Ignav API, including available flight details, schedules, and displayed fares.
- **Weather Tool:** Provides weather information through the configured weather integration.
- **Web Search:** Searches the web for additional travel information.
- **Streamlit Interface:** Provides an interactive web application.
- **API Error Handling:** Handles Gemini API quota errors and other supported failure cases.
- **Environment Configuration:** Keeps API keys in environment variables or deployment secrets.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| AI Agent Framework | LangChain |
| Large Language Model | Google Gemini |
| Knowledge Retrieval | LangChain and ChromaDB |
| Embeddings | Google Gemini embeddings |
| Flight Search | Ignav API |
| Weather | Configured weather API integration |
| Configuration | python-dotenv |
| Version Control | Git and GitHub |

## 📁 Project Structure

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
├── database/
│   ├── crud.py
│   ├── database.py
│   └── models.py
├── rag/
│   ├── embeddings.py
│   ├── loader.py
│   ├── qa.py
│   ├── retriever.py
│   ├── splitter.py
│   └── vectorstore.py
├── travel_api/
│   ├── client.py
│   └── parser.py
├── app.py
├── requirements.txt
└── README.md
```

*Note: The structure above highlights the main application modules. Additional files, including tests and configuration files, may also be present.*

## 🚀 Installation and Setup

### Prerequisites

- Python installed on your computer
- Git installed
- API credentials for the integrations you want to use

### 1. Clone the Repository

```bash
git clone https://github.com/Jayesh0205/AI-Travel-Concierge.git
cd AI-Travel-Concierge
```

### 2. Create a Virtual Environment

On Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```cmd
python -m pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root directory.

Add your own API credentials:

```dotenv
GOOGLE_API_KEY=your_google_api_key
IGNAV_API_KEY=your_ignav_api_key
```

Replace the example values with your actual credentials. Do not commit your real API keys to GitHub.

Other integrations may require additional configuration, depending on the current application settings.

### 5. Run the Application

```cmd
streamlit run app.py
```

Streamlit will provide a local URL that you can open in your browser.

## ⚙️ How It Works

1. The user submits a travel-related request through the Streamlit interface.
2. The LangChain agent interprets the request and selects an appropriate available tool when needed.
3. For travel knowledge questions, the RAG pipeline retrieves relevant information from the configured travel documents.
4. For flight searches, the flight-search tool requests available results from the Ignav API.
5. Weather and web-search tools provide additional information when appropriate.
6. Google Gemini generates a response using the available information.
7. The application displays the result in the Streamlit interface.

## 🌐 Project Links

- **GitHub Repository:** https://github.com/Jayesh0205/AI-Travel-Concierge
- **Deployed Application:** https://novatrip-jayesh.streamlit.app

## 🔐 Security

- Store API credentials in `.env` locally and in the deployment platform's secrets configuration when deployed.
- Never commit `.env` or expose API keys in screenshots, logs, or public repositories.
- If an API key is accidentally exposed, revoke or rotate it through the relevant provider.

## ⚠️ Limitations

- AI-generated responses may contain inaccuracies and should be verified when making travel decisions.
- Flight schedules, displayed fares, and availability may change. Confirm the details with the provider before booking.
- Flight search depends on valid Ignav API credentials, API availability, and returned inventory.
- Google Gemini usage is subject to model availability, quota, and API limits.
- Document upload currently supports `.txt` files.
- The application provides travel information and flight-search results; it does not itself guarantee a booking.

## 🔮 Future Improvements

- Expand travel-document formats and improve retrieval quality.
- Add itinerary export options.
- Improve automated testing and error monitoring.
- Enhance the user interface and travel-planning workflow.
- Expand travel integrations and improve handling of API failures.
