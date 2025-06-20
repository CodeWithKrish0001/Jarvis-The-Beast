# Jarvis: AI Voice & Text Assistant

Jarvis is a modular, extensible AI assistant inspired by Tony Stark's J.A.R.V.I.S. It supports text and voice interaction, code execution, weather, web search, image generation, Telegram messaging, and more. The project is structured for easy addition of new tools and models.

---

## Features
- **Text Mode**: Chat with Jarvis using your keyboard.
- **Voice Mode**: Speak to Jarvis and get spoken responses (multiple STT/TTS models supported).
- **Streaming Responses**: Both text and voice streaming.
- **Auto Code Execution**: Jarvis can generate and execute Python code for tasks.
- **Weather, Web Search, Image Generation**: Built-in tools for common tasks.
- **Telegram Integration**: Send/read messages via Telegram.
- **Modular Models**: Easily swap text, TTS, and STT models via config.
- **Persistent Chat History**: Remembers conversations and tool calls.

---

## Project Structure
```
Jarvis/
  main.py                # Main entry point (mode selection)
  config.py              # Model and path configuration
  data/                  # AI data, code, and chat history
  gui/                   # GUI (PyQt5, not yet complete)
  models/                # Model implementations (text, tts, stt)
  tools/                 # Tool plugins (weather, web, image, etc.)
  utils/                 # Utility functions and helpers
```

---

## Requirements
All dependencies are listed in `requirements.txt`. Major libraries include:
- `playsound` (audio playback)
- `requests`, `aiohttp`, `trafilatura` (web, scraping)
- `python-dotenv` (env vars)
- `PyQt5` (GUI, not yet complete)
- `openai`, `google-generativeai` (AI APIs)
- `pyrogram`, `fuzzywuzzy` (Telegram)
- `pygame` (auto code execution, games)
- `AppOpener` (open/close apps)
- `speech_recognition`, `mtranslate` (STT)
- `selenium` (alternative STT)
- `edge_tts`, `elevenlabs` (TTS)

Some dependencies are only needed for specific models/tools. See below.

---

## Setup
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables** (for APIs like Gemini, OpenAI, Telegram, ElevenLabs, etc.)
   - Create a `.env` file in the root directory with your API keys:
     - `GEMINI_API_KEY`, `OPENAI_API_KEY`, `TOGETHER_API_KEY`, `GROQ_API_KEY`
     - `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION_NAME`
     - `ELEVENLABS_API_KEY`

> 💬 **Bonus:** Contanct me if you want free **OpenAI** and **Together.ai** API keys

4. **Run Jarvis**:
   ```bash
   python main.py
   ```

---

## Usage
- Choose between Text, Voice, or Streaming modes at startup.
- Use the config file to select which text, TTS, and STT models to use.
- Some features (like Telegram, image generation, or code execution) require API keys or special setup.

---

## Notes
- **GUI is not yet complete.** The graphical interface (PyQt5) is under development and will be added soon.
- For voice and streaming features, ensure your microphone and speakers are working.
- Some tools require API keys (Gemini, OpenAI, Telegram, ElevenLabs, etc.).
- Some tools auto-install their own dependencies at runtime (see auto_code_execute.py).
- Platform-specific: Some features (like AppOpener, os.startfile) are Windows-only.

---

## Optional/Model-Specific Dependencies
- **STT**: `speech_recognition`, `mtranslate`, `selenium`
- **TTS**: `edge_tts`, `elevenlabs`
- **Games/Auto Code**: `pygame`
- **Telegram**: `pyrogram`, `fuzzywuzzy`
- **Web Scraping**: `aiohttp`, `trafilatura`

---

## Contributing
Pull requests and suggestions are welcome!

## License
MIT License 