from pyrogram import Client
from pyrogram.errors import RPCError
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
session_name = os.getenv("TELEGRAM_SESSION_NAME")

app = Client(session_name, api_id=api_id, api_hash=api_hash)

last_sent_messages = {}

def resolve_chat_id(app, target_name: str):
    dialogs = app.get_dialogs()
    best_match = None
    highest_score = 0

    for dialog in dialogs:
        name = dialog.chat.title or (dialog.chat.first_name or "") + " " + (dialog.chat.last_name or "")
        score = fuzz.partial_ratio(target_name.lower(), name.lower())
        if score > highest_score:
            highest_score = score
            best_match = dialog.chat.id

    return best_match if highest_score >= 60 else None

def telegram_tool(operation: str, target_name: str = None, message: str = None, message_id: int = None):
    try:
        with app:
            if operation == "send_message":
                if target_name and message:
                    chat_id = resolve_chat_id(app, target_name)
                    if not chat_id:
                        return f"Could not find a chat matching: {target_name}"
                    sent = app.send_message(chat_id, message)
                    last_sent_messages[chat_id] = sent.id
                    return f'The message "{message}" has been sent to {target_name}, Sir.'
                else:
                    return "target_name and message are required for sending messages."

            elif operation == "delete_message":
                if not target_name:
                    return "target_name is required to delete a message."
                chat_id = resolve_chat_id(app, target_name)
                if not chat_id:
                    return f"Could not find a chat matching: {target_name}"

                mid = message_id or last_sent_messages.get(chat_id)
                if not mid:
                    return f"Sorry, Sir. No recent message ID found to delete in {target_name}."

                app.delete_messages(chat_id, message_ids=mid)
                return f"The last message has been deleted from {target_name}, Sir."

            elif operation == "read_messages":
                if not target_name:
                    return "target_name is required to read messages."
                chat_id = resolve_chat_id(app, target_name)
                if not chat_id:
                    return f"Could not find a chat matching: {target_name}"
                messages = app.get_chat_history(chat_id, limit=5)
                return [
                    {
                        "message_id": msg.message_id,
                        "sender": msg.from_user.first_name if msg.from_user else "Unknown",
                        "text": msg.text
                    } for msg in messages
                ]

            elif operation == "get_unread_count":
                dialogs = app.get_dialogs()
                unread_total = sum(dialog.unread_messages_count for dialog in dialogs)
                return f"Total unread messages: {unread_total}"

            elif operation == "get_chats":
                chats = app.get_dialogs(limit=10)
                return [{"chat_id": dialog.chat.id, "title": dialog.chat.title or dialog.chat.first_name} for dialog in chats]

            else:
                return "Invalid operation."

    except RPCError as e:
        return f"Telegram API error: {e}"
    except Exception as e:
        return f"Error: {e}"

tool_definition = {
    "type": "function",
    "function": {
        "name": "telegram_tool",
        "description": "Performs Telegram operations like sending, reading, deleting messages (even last sent), getting unread counts, and listing chats. Uses fuzzy matching for target name.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The operation to perform.",
                    "enum": [
                        "send_message",
                        "read_messages",
                        "delete_message",
                        "get_unread_count",
                        "get_chats"
                    ]
                },
                "target_name": {
                    "type": "string",
                    "description": "Name of the user or group to operate on (fuzzy matched from previous chats). Required for send_message, read_messages, and delete_message."
                },
                "message": {
                    "type": "string",
                    "description": "Text to send. Required for send_message."
                },
                "message_id": {
                    "type": "integer",
                    "description": "Message ID to delete. Optional if you want to delete the last sent message."
                }
            },
            "required": ["operation"]
        }
    }
}


if __name__ == "__main__":
    print("Telegram client is ready. You can now use the telegram_tool function.")
    response = telegram_tool("send_message", target_name="Vortex", message="Hello!")
    print(response)
