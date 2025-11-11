import json, os
from config import DB_FILE

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except:
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)