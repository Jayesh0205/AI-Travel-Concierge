\# NovaTrip – API Documentation



\## 1. Overview



NovaTrip integrates external APIs and internal application tools to collect travel information and support AI-powered itinerary generation.



\## 2. IGNAV Flight API



\*\*Purpose:\*\* Retrieve flight information based on travel details.



\- Base URL: `https://ignav.com/api`

\- Endpoint: `POST /fares/one-way`

\- Authentication: API key through the `X-Api-Key` header.

\- Content type: JSON.



\### Request Parameters



| Parameter | Description |

|---|---|

| origin | Origin airport code |

| destination | Destination airport code |

| departure\_date | Departure date |

| market | Market identifier (IN) |



\### Functionality



The application sends flight search parameters to IGNAV and processes the returned response to display available flight information.



Errors such as missing API credentials, HTTP failures, and connection problems are handled by the application.



\## 3. Open-Meteo Weather API



\*\*Purpose:\*\* Retrieve current weather and forecast information for a destination.



\### Services Used



\- Geocoding API: Resolves destination names into coordinates.

\- Forecast API: Retrieves weather information using latitude and longitude.



\### Weather Information



The application can retrieve:



\- Temperature

\- Relative humidity

\- Apparent temperature

\- Precipitation

\- Wind speed



The application uses these details to provide weather context for travel planning.



\## 4. DuckDuckGo Web Search



\*\*Purpose:\*\* Collect additional travel information from web search results.



The application uses the DDGS Python library.



\### Search Configuration



\- Maximum results: 5

\- Output: Search title, summary, and URL.



The returned information is included in the travel research stage.



\## 5. Internal AI Tools



NovaTrip also provides internal tools through LangChain.



| Tool | Purpose |

|---|---|

| travel\_knowledge\_search | Retrieves relevant travel information through RAG |

| itinerary\_planner | Prepares itinerary planning instructions |

| web\_search | Performs web research |

| current\_weather | Retrieves destination weather |

| flight\_search | Retrieves flight information |



\## 6. Agent Workflow Integration



The LangGraph workflow coordinates the application tools through four stages:



1\. Analyze the travel request.

2\. Research relevant information using available tools.

3\. Generate the itinerary using Google Gemini.

4\. Save the generated search result.



\## 7. Error Handling



The application includes error handling for:



\- Missing API credentials.

\- API connection failures.

\- HTTP errors.

\- Empty search results.

\- Unavailable travel information.

\- LLM quota and rate-limit errors.



The application aims to provide graceful responses when external services are unavailable.



\## 8. Security Considerations



\- API credentials are stored in environment variables.

\- API keys should not be committed to the public GitHub repository.

\- External requests use timeouts.

\- Sensitive configuration values should be maintained in environment files.



\## 9. Conclusion



The API integrations allow NovaTrip to combine external travel information with AI-powered research and itinerary generation.

