import speech_recognition as sr
import mtranslate as mt
from models.config import save_stt_location

InputLanguage = "en"

def QueryModifier(query):
    new_query = query.lower().strip()
    question_words = ["how", "what", "when", "where", "who", "which", "why", "can you", "whom", "whose", "what's", "where's"]
    if any(word + " " in new_query for word in question_words):
        if new_query[-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if new_query[-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def UniversalTranslator(text):
    english_translation = mt.translate(text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listining...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language=InputLanguage)

        if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
            format_text =  QueryModifier(text)
            with open(save_stt_location, "w", encoding="utf-8") as f:
                f.write(format_text)
            return format_text
        
        else:
            return QueryModifier(UniversalTranslator(text))

    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        if result:
            print(result)
