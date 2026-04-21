import json
import asyncio
import os
import tempfile

lock = asyncio.Lock()

with open("src/data/persistent_vars.json") as f:
    persistent_vars = json.load(f)

async def save_persistent():
    async with lock:
        filename = "src/data/persistent_vars.json"
        dir_name = os.path.dirname(filename) or "."

        with tempfile.NamedTemporaryFile("w", delete=False, dir=dir_name) as tmp:
            json.dump(persistent_vars, tmp, indent=4)
            temp_name = tmp.name

        os.replace(temp_name, filename)