
import json

with open("scraped/lua_bugs.json", "r") as f:
    lines = json.load(f)
    i = 0
    for l in lines:
        with open(f"crawled/lua/{i}.json", "w") as w:
            w.write(json.dumps(l))
        i += 1
