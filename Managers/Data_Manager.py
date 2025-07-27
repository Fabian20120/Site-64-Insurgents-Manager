import json
import os
from .Platform_Manager import Get_Full_Path

def Set_Variable_By_UserId(Variable, Value, UserId):
    Economy = Get_Economy_By_UserId(UserId)
    Economy[Variable] = Value
    Save_Economy_By_UserId(Economy, UserId)

def Get_Variable_By_UserId(Variable, UserId):
    Economy = Get_Economy_By_UserId(UserId)
    if Economy[Variable]:
        return Economy[Variable]
    else:
        return None

def Get_Economy_By_UserId(UserId):
    path = str(Get_Full_Path(f"Backend\Economy/{UserId}.json"))
    path = path.split("Manager")
    path = path[0] + f"Manager\\Backend\\Economy\\{UserId}.json"
    return load_json(path)

def Save_Economy_By_UserId(Economy, UserId):
    path = str(Get_Full_Path(f"Backend\Economy/{UserId}.json"))
    path = path.split("Manager")
    path = path[0] + f"Manager\\Backend\\Economy\\{UserId}.json"
    save_json(path, Economy)

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        save_json(file_path, {})
        return {}
            
def save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=True)
    except Exception as e:
        print(e)
        return f"error: \n{e}"
    finally:
        return "successful"
        
    