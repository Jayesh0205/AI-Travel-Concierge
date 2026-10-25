from agent.tools import create_tools

tools = create_tools()
flight_tool = next(t for t in tools if t.name == "flight_search")

result = flight_tool.invoke({
    "origin": "BOM",
    "destination": "DEL",
    "departure_date": "2026-11-15",
})

from pprint import pprint
pprint(result)

print(result)