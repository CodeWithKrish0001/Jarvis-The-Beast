from AppOpener import open

def open_app(app_name: str) -> str:
    try:
        open(app_name, match_closest=True)
        return f"Opening {app_name}..."
    except Exception as e:
        return f"Error: {str(e)}"

tool_definition = {
    "type": "function",
    "function": {
        "name": "open_app",
        "description": "Opens an application by its name on the local system. It only opens app nothing else like if user said open youtube now it is commen sense that youtube has no app so it can't open youtube so it use auto_code_execute function not this open_app function.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The name of the application to open."
                }
            },
            "required": ["app_name"]
        }
    }
}
