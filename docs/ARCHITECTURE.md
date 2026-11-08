\# NovaTrip – System Architecture Documentation



\## 1. Project Overview



NovaTrip is an AI-powered Travel Concierge that helps users research destinations and generate personalized travel itineraries. It combines Large Language Models, Retrieval-Augmented Generation (RAG), external APIs, and database integration.



\## 2. Technology Stack



| Component | Technology |

|---|---|

| Frontend | Streamlit |

| Programming Language | Python |

| Large Language Model | Google Gemini |

| Agent Framework | LangChain |

| Workflow Orchestration | LangGraph |

| RAG | ChromaDB |

| Embeddings | Google Gemini Embeddings |

| Database | PostgreSQL |

| Flight Information | IGNAV API |

| Weather Information | Open-Meteo API |

| Web Research | DuckDuckGo Search |

| Testing | Pytest |



\## 3. System Architecture



The application follows a modular architecture:



\*\*User Interface → Agent Workflow → Research Tools → AI Response → Database Storage\*\*



\### Main Components



1\. \*\*Streamlit Interface:\*\* Accepts travel requests, displays responses, and supports TXT document uploads.

2\. \*\*Agent Layer:\*\* Uses Google Gemini and LangChain to process travel requests.

3\. \*\*LangGraph Workflow:\*\* Coordinates the analyze, research, generate, and save stages.

4\. \*\*RAG Layer:\*\* Retrieves relevant information from travel documents using embeddings and ChromaDB.

5\. \*\*Travel API Layer:\*\* Connects to external services for flight, weather, and web research.

6\. \*\*Database Layer:\*\* Uses PostgreSQL to store structured records and API activity.



\## 4. Workflow Execution



The LangGraph workflow consists of four main stages:



1\. \*\*Analyze:\*\* Processes the user's travel request.

2\. \*\*Research:\*\* Collects relevant travel knowledge, web information, weather information, and flight information when the required details are provided.

3\. \*\*Generate:\*\* Uses Google Gemini to generate a personalized travel itinerary based on the collected research.

4\. \*\*Save:\*\* Stores the travel search and generated response in the database.



\## 5. Retrieval-Augmented Generation



NovaTrip uses RAG to provide context-aware travel information.



\- Loads travel information from TXT documents.

\- Splits documents into smaller chunks.

\- Generates vector embeddings.

\- Stores the embeddings in ChromaDB.

\- Retrieves relevant chunks for user questions.

\- Uses retrieved context to generate grounded AI responses.



\## 6. Database Architecture



PostgreSQL contains the following main tables:



| Table | Purpose |

|---|---|

| users | Stores user information |

| trips | Stores structured trip information |

| saved\_searches | Stores travel queries and responses |

| api\_activity | Records external API activity |



Foreign keys connect user records with their associated trips and saved searches.



\## 7. External API Integrations



\- \*\*IGNAV:\*\* Retrieves flight information based on origin, destination, and departure date.

\- \*\*Open-Meteo:\*\* Provides weather information for travel destinations.

\- \*\*DuckDuckGo:\*\* Supports web-based travel research.



The application handles API errors and unavailable responses to improve reliability.



\## 8. Testing



Pytest is used to test the database and workflow components. The current automated test suite contains 11 passing tests.



\## 9. Future Scope



\- Voice-based travel interaction.

\- Conditional and parallel agent execution.

\- Additional travel service integrations.

\- Enhanced trip management and personalization.

\- Improved monitoring and analytics.



\## 10. Conclusion



NovaTrip demonstrates the practical integration of Agentic AI, RAG, LangGraph, external APIs, and PostgreSQL to build an intelligent travel-planning assistant.

