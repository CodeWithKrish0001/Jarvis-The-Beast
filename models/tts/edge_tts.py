import asyncio
import os
from edge_tts import Communicate
from models.config import save_tts_location
from utils.common.ensure_save_directory import ensure_save_directory
from config import edge_tts_voice

async def generate_tts_async(text):
    ensure_save_directory(save_tts_location)

    tts = Communicate(text=text, voice=edge_tts_voice)
    await tts.save(save_tts_location)
    return save_tts_location

def generate_tts(text):
    try:
        return asyncio.run(generate_tts_async(text))
    except Exception as e:
        print(f"Error generating voiceover: {e}")
        return None

if __name__ == "__main__":
    text = input("Enter text for tts: ")
    audio_path = generate_tts(text)

    if audio_path:
        print(f"tts generated successfully at: {audio_path}")
    else:
        print("Failed to generate tts")
