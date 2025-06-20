import json
import os
from models.config import chat_history_location

def load_chat_history():
    if os.path.exists(chat_history_location):
        with open(chat_history_location, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_chat_history(history):
    with open(chat_history_location, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
