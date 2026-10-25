from pprint import pprint
from travel_api.client import search_flights

result = search_flights("BOM", "DEL", "2026-11-15")
pprint(result)