import requests
from models.config import save_tts_location
from config import openaifm_voice
from utils.common.ensure_save_directory import ensure_save_directory

def generate_tts(text):
    ensure_save_directory(save_tts_location)

    url = "https://www.openai.fm/api/generate"
    payload = {
        "input": text,
        "voice": openaifm_voice,
        "vibe": "null"
    }

    try:
        files = {key: (None, value) for key, value in payload.items()}
        response = requests.post(url, files=files, timeout=30)

        if response.status_code == 200:
            with open(save_tts_location, "wb") as f:
                f.write(response.content)

            return save_tts_location
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
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
