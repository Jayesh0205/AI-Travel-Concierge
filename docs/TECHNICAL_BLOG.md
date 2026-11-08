\# Building NovaTrip: An AI-Powered Travel Concierge Using Agentic AI



\## Introduction



Travel planning often requires gathering information from multiple sources, checking weather conditions, researching destinations, and organizing itineraries.



To simplify this process, we developed \*\*NovaTrip\*\*, an AI-powered Travel Concierge as part of our Agentic AI internship at Capabl.



The project demonstrates how Large Language Models, agent workflows, Retrieval-Augmented Generation, external APIs, and databases can work together to support intelligent travel planning.



\## Technology Stack



We used the following technologies:



\- Python for application development.

\- Streamlit for the user interface.

\- Google Gemini as the Large Language Model.

\- LangChain for AI tool integration.

\- LangGraph for workflow orchestration.

\- ChromaDB for vector storage.

\- Google Gemini Embeddings for document embeddings.

\- PostgreSQL for structured data and activity logging.

\- IGNAV for flight information.

\- Open-Meteo for weather information.

\- DuckDuckGo for web research.



\## How NovaTrip Works



NovaTrip follows a multi-step workflow:



1\. Analyze the user's travel request.

2\. Research travel information using integrated tools.

3\. Generate a personalized itinerary using Google Gemini.

4\. Save the travel search and generated response.



This workflow is coordinated using LangGraph.



\## Implementing Retrieval-Augmented Generation



One of the important features is RAG.



We load travel information from TXT documents, split it into smaller chunks, generate embeddings, and store them in ChromaDB.



When a user asks a travel-related question, the application retrieves relevant information and uses it as context for generating a response.



This helps the application provide answers grounded in the available travel documents.



\## External API Integration



NovaTrip integrates multiple external services:



\- IGNAV provides flight information.

\- Open-Meteo provides destination weather information.

\- DuckDuckGo supports travel-related web research.



These integrations allow the agent to collect information from different sources before generating recommendations.



\## Database Integration



PostgreSQL supports structured storage for users, trips, saved searches, and API activity.



API activity records help track providers, execution times, and success information.



\## Challenges and Learning



During development, we worked on several practical engineering challenges:



\- Integrating Google Gemini with LangChain.

\- Managing API errors and quota limitations.

\- Building a document retrieval pipeline.

\- Coordinating multiple tools through LangGraph.

\- Connecting PostgreSQL with the application.

\- Testing individual components and workflow integration.



These challenges helped us understand how different parts of an Agentic AI application work together.



\## Conclusion



NovaTrip demonstrates the practical application of Agentic AI in travel planning.



Through this project, we gained experience with LLM integration, RAG, vector databases, workflow orchestration, external APIs, PostgreSQL, and automated testing.



The project provided valuable hands-on experience in building an end-to-end AI-powered application.



\*\*Project:\*\* NovaTrip – AI Travel Concierge



\*\*Repository:\*\* https://github.com/Jayesh0205/AI-Travel-Concierge

