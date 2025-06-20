import importlib
from config import TEXT_MODEL

text_module = importlib.import_module(f"models.text_generation.{TEXT_MODEL}")

def stream_response(query):
    return text_module.stream_response(query)
