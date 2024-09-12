import json
import os


def search_user(email):
    json_path = r'/flask.json'

    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, 'r') as f:
            file = json.load(f)
    except (json.JSONDecodeError, Exception):
        return None
    user = file.get(email, None)
    return user

def create_user(email, password):
    json_path = r'/flask.json'

    if not os.path.exists(json_path):
        with open(json_path, 'w') as f:
            json.dump({}, f)

    # Load the JSON data
    with open(json_path, 'r') as f:
        try:
            file = json.load(f)
        except json.JSONDecodeError:
            file = {}

    file[email] = password

    with open(json_path, 'w') as f:
        json.dump(file, f, indent=4)
