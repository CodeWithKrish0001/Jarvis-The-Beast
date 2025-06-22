import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
from models.config import save_tts_location
from config import eleven_voice, eleven_voice_model
from utils.common.ensure_save_directory import ensure_save_directory
import asyncio

load_dotenv()
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

VOICE_ID = eleven_voice
MODEL_ID = eleven_voice_model

async def generate_tts_async(text, voice_id=VOICE_ID, model_id=MODEL_ID):
    ensure_save_directory(save_tts_location)
    audio_generator = elevenlabs.text_to_speech.stream(
        text=text,
        voice_id=voice_id,
        model_id=model_id
    )
    with open(save_tts_location, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)
    return save_tts_location

def generate_tts(text):
    try:
        return asyncio.run(generate_tts_async(text))
    except Exception as e:
        print(f"Error generating voiceover: {e}")
        return None

# ========== STREAM TTS IN REALTIME USING mpv ==========
def play_streaming_tts(text, voice_id=VOICE_ID, model_id=MODEL_ID):
    try:
        audio_generator = elevenlabs.text_to_speech.stream(
            text=text,
            voice_id=voice_id,
            model_id=model_id
        )
        stream(audio_generator)
    except Exception as e:
        print("Streaming TTS error:", e)
