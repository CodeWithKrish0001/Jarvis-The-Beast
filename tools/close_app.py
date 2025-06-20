from AppOpener import close

def close_app(app_name: str) -> str:
    try:
        close(app_name, match_closest=True)
        return f"Closing {app_name}..."
    except Exception as e:
        return f"Error: {str(e)}"

tool_definition = {
    "type": "function",
    "function": {
        "name": "close_app",
        "description": "Closes an application by its name on the local system.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The name of the application to close."
                }
            },
            "required": ["app_name"]
        }
    }
}