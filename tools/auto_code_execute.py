import google.generativeai as genai
import os
import json
import subprocess
from dotenv import load_dotenv
from models.config import auto_code_location, auto_code_execute_chat_history_location

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

HISTORY_FILE = auto_code_execute_chat_history_location

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": 1.2,
        "top_p": 0.9,
        "top_k": 50
    },
    system_instruction=(
        """
        You are an auto code execution assistant. Your task is to write Python code based on the user's prompt.

        Instructions:
        - Always respond with Python code only nothing else you have to only write code dont give any instrutions strictly disable it.
        - Do not include any explanation or additional text—just the code.
        - Only use print() when strictly needed not also with expect exeption handling like: except Exception as e:
          print(f"Error opening Notepad: {e}")
        - If the code uses any external library (not included in Python's standard library), include the necessary pip installation command using `subprocess` and `sys` to auto-install it.
        Example pattern for auto-install:
        - and remember dont write if __name__ == "__main__": at the end of the code, just write the code that is needed to execute the task.

        try:
            import some_library
        except ImportError:
            import subprocess, sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "some_library"])
            import some_library

        - Maintain this behavior for all user prompts that require external libraries.

        Examples:

        Prompt: "Open Chrome and search for Elon Musk"

        Response:
        import webbrowser

        search_query = "elon musk"
        search_url = f"https://www.google.com/search?q={search_query}"
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        webbrowser.get(chrome_path).open_new_tab(search_url)

        Prompt: "Close YouTube"

        Response:
        import sys
        try:
            import pygetwindow as gw
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygetwindow"])
            import pygetwindow as gw

        youtube_window = gw.getWindowsWithTitle('YouTube')[0]
        youtube_window.close()

        Prompt: "Play Supreme song"

        Response:
        import subprocess
        import sys
        
        try:
            import pywhatkit
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywhatkit"])
            import pyautogui

        def play(song):
            pywhatkit.playonyt(song)

        play("Supreme song")
        """
    )
)

def serialize_history(history):
    serialized = []
    for msg in history:
        if hasattr(msg, 'parts'):
            content = " ".join([part.text for part in msg.parts if hasattr(part, 'text')])
        else:
            content = None 
        serialized.append({
            "role": getattr(msg, "role", None),
            "content": content
        })
    return serialized

def save_chat_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(serialize_history(history), f, ensure_ascii=False, indent=2)


def load_chat_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                formatted_history = []
                for entry in data:
                    if "role" in entry and "content" in entry:
                        formatted_history.append(
                            genai.types.ContentDict(
                                parts=[genai.types.PartDict(text=entry["content"])],
                                role=entry["role"]
                            )
                        )
                return formatted_history
            except json.JSONDecodeError:
                return []
    return []

chat = model.start_chat(history=load_chat_history())

TEMP_FILE_PATH = auto_code_location

def auto_code_execute(prompt: str) -> str:
    response = chat.send_message(prompt)
    code = response.text.strip()

    save_chat_history(chat.history)

    if code.startswith("```python"):
        code = code.replace("```python", "").replace("```", "").strip()

    with open(TEMP_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        if os.name == 'nt':
            if 'input(' in code or 'print(' in code:
                os.system(f'start cmd /k python "{TEMP_FILE_PATH}"')
            else:
                subprocess.Popen(
                    ["python", TEMP_FILE_PATH],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
        elif os.name == 'posix':
            os.system(f'gnome-terminal -- bash -c "python3 \\"{TEMP_FILE_PATH}\\"; exec bash"')
        else:
            return "❌ Unsupported OS for execution."

        return "✅ Code is running."

    except Exception as e:
        return f"❌ Execution Error:\n{e}"


tool_definition = {
    "type": "function",
    "function": {
        "name": "auto_code_execute",
        "description": "Generates and executes Python code based on a natural language prompt using Gemini API. Use it for anything like, searching for something in web browser, or any other task that can be done with Python code in which you have to do a task which you dont know how to do so it write code and auto execute it. Like user said open chrome and search for elon musk, it will write code to open chrome and search for elon musk. Another example like if user say I want to play snake game, it will write code for a snake game in python and execute it. Or like if user say open chatgpt.com, so it is common sense that you dont use open_app function as it only open system apps, and this is a website so you use this auto_code_execute function",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The user prompt that describes the task to generate Python code for. never ever skip this parameter, always provide a prompt to generate code for else it throw err"
                }
            },
            "required": ["prompt"]
        }
    }
}