import requests

def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Weather data could not be fetched."
    except Exception as e:
        return f"Error: {str(e)}"

tool_definition = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Gets current weather information for a specified city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city to get the weather for."
                }
            },
            "required": ["city"]
        }
    }
}

