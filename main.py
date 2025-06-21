from config import TEXT_MODEL, TTS_MODEL, STT_MODEL
import importlib
from playsound import playsound
import os
import time
from models.text_generation import streaming_wrapper
from models.config import ensure_directories_exist
import pygame

text_module = importlib.import_module(f"models.text_generation.{TEXT_MODEL}")
tts_module = importlib.import_module(f"models.tts.{TTS_MODEL}")
stt_module = importlib.import_module(f"models.stt.{STT_MODEL}")

def play_audio(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

def text_mode():
    print("\n=== Text Mode (Streaming Response) ===")
    while True:
        user_input = input("You: ").strip()
        if any(word in user_input.lower() for word in ["exit jarvis", "quit jarvis", "stop now jarvis", "bye jarvis"]):
            print("Exiting text mode...")
            return False

        print("Jarvis:", end=" ", flush=True)
        response_text = ""
        for chunk in streaming_wrapper.stream_response(user_input):
            if chunk:
                print(chunk, end="", flush=True)
                response_text += chunk
        print()

def voice_mode():
    print("\n=== Voice Mode ===")
    while True:
        print("\nListening... (Say 'exit' to quit voice mode)")
        user_input = stt_module.SpeechRecognition()

        if not user_input:
            continue

        print("You:", user_input)

        if any(word in user_input.lower() for word in ["exit", "quit", "stop", "bye"]):
            print("Exiting voice mode...")  
            return False

        response = text_module.generate_response(user_input)
        if response:
            print("Jarvis:", response)
            audio_path = tts_module.generate_tts(response)

            timeout = 10
            start_time = time.time()
            while (not os.path.isfile(audio_path) or os.path.getsize(audio_path) == 0) and time.time() - start_time < timeout:
                time.sleep(0.1)

            if os.path.isfile(audio_path) and os.path.getsize(audio_path) > 0:
                play_audio(audio_path)
                os.remove(audio_path)
            else:
                print("Audio file not ready, cannot play.")
        else:
            print("Failed to generate response.")

def voice_mode_streaming():
    print("\n=== Voice Mode (Streaming) ===")
    while True:
        user_input = stt_module.SpeechRecognition()

        if not user_input:
            print("\nListening... (Say 'exit' to quit voice mode)")
            continue

        print("You:", user_input)

        if any(word in user_input.lower() for word in ["exit", "quit", "stop", "bye"]):
            print("Exiting streaming voice mode...")
            return False

        print("Jarvis:", end=" ", flush=True)
        response_text = ""
        for chunk in streaming_wrapper.stream_response(user_input):
            if chunk:
                print(chunk, end="", flush=True)
                response_text += chunk

        print()
        if response_text.strip():
            tts_module.play_streaming_tts(response_text.strip())

        print("\nListening... (Say 'exit' to quit voice mode)")

def main():
    while True:
        print("\nChoose mode:")
        print("1. Text Mode")
        print("2. Voice Mode")
        print("3. Voice Mode (Streaming)")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            if text_mode() is False:
                break
        elif choice == "2":
            if voice_mode() is False:
                break
        elif choice == "3":
            if voice_mode_streaming() is False:
                break
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    ensure_directories_exist()
    main()
