import json
from models.config import chat_history_location

def save_conversation(conversation):
    with open(chat_history_location, 'w', encoding='utf-8') as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)
