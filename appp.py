import urllib.request
import json

src = "https://padax.github.io/taipei-day-trip-resources/taipei-attractions-assignment.json"

with urllib.request.urlopen(src) as response:
    # data = json.load(response.read().decode("utf-8"))
    data = json.load(response)
    print(data)
