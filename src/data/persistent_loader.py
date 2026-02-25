import json

with open("src/data/persistent_vars.json") as f:
    persistent_vars = json.load(f)

def save_persistent():
    with open("src/data/persistent_vars.json", 'w') as f:
        json.dump(persistent_vars, f, indent=4)