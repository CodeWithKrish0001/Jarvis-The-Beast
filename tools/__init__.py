from tools.get_weather import get_weather, tool_definition as weather_def
from tools.web_search import web_search, tool_definition as search_def
from tools.image_generator import generate_image, tool_definition as image_gen_def
from tools.open_app import open_app, tool_definition as open_app_def
from tools.close_app import close_app, tool_definition as close_app_def
from tools.auto_code_execute import auto_code_execute, tool_definition as auto_code_def
from tools.telegram import telegram_tool, tool_definition as telegram_def

tool_registry = {
    "get_weather": get_weather,
    "web_search": web_search,
    "generate_image": generate_image,
    "open_app": open_app,
    "close_app": close_app,
    "auto_code_execute": auto_code_execute,
    "telegram_tool": telegram_tool
}

tool_definitions = [
    weather_def,
    search_def,
    image_gen_def,
    open_app_def,
    close_app_def,
    auto_code_def,
    telegram_def
]
