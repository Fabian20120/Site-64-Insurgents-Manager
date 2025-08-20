import json
import os

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    return {}

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def load_user_economy(user_id, economy):
    file_path = f"DataStore/Economys/UserData/{user_id}.json"
    economy_data = load_json(file_path)
    return economy_data.get(economy, 0)

def get_user_xp(user_id):
    file_path = f"DataStore/XP/UserData/{user_id}.json"
    xp_data = load_json(file_path)
    return xp_data.get("xp", 0)
