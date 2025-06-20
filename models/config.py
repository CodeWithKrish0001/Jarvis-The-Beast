from utils.common.ensure_save_directory import ensure_save_directory
import os

save_res_location = "data/ai/response.txt" 
save_tts_location = "data/ai/tts.mp3"
save_stt_location = "data/ai/stt.txt"
image_generation_location = "data/ai/images"
auto_code_location = "data/ai/code/auto_code.py"
auto_code_execute_chat_history_location = "data/ai/code/chat_history.json"
chat_history_location = "data/ai/memory/chat_history.json"

def ensure_directories_exist():
    paths = [
        save_res_location,
        save_tts_location,
        save_stt_location,
        auto_code_location,
        auto_code_execute_chat_history_location,
        chat_history_location,
        image_generation_location,
    ]
    for path in paths:
        ensure_save_directory(path)
