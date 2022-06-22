from __future__ import print_function
import json

data = {}
# Open JSON file
with open("analyze.json", "r") as file:
    # parse file
    data = json.loads(file.read())
    print(data)
    d = json.dumps(data)
    print(d)

