import re
import ast
from tools import tool_registry

def execute_fake_tool_call_if_present(content: str) -> str:
    """
    Detects and executes a fake tool call like [tool_name(...)] once,
    then removes it from content to prevent repeated execution.
    """
    pattern = r"\[([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)\]"
    match = re.search(pattern, content)
    if not match:
        return content

    tool_name, args_str = match.groups()

    if tool_name not in tool_registry:
        return f"{content}\n\n⚠️ Tool '{tool_name}' not available."

    try:
        args = ast.literal_eval("dict(" + args_str + ")")
        result = tool_registry[tool_name](**args)

        cleaned_content = content.replace(match.group(0), "").strip()

        return f"{cleaned_content}\n\n✅ Tool '{tool_name}' executed.\nResult: {result}"
    except Exception as e:
        return f"{content}\n\n⚠️ Failed to execute tool '{tool_name}': {e}"
