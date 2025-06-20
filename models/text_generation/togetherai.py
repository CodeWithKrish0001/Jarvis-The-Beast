import os
import json
import openai
from dotenv import dotenv_values
from models.config import save_res_location
from utils.models.system_prompt import system_prompt
from utils.common.ensure_save_directory import ensure_save_directory
from utils.models.available_tools import get_available_tools
from utils.common.chat_history import load_chat_history, save_chat_history
from utils.models.execute_fake_call import execute_fake_tool_call_if_present
from tools import tool_registry

env = dotenv_values(".env")
TOGETHER_API_KEY = env.get("TOGETHER_API_KEY")
if not TOGETHER_API_KEY:
    raise ValueError("TOGETHER_API_KEY not found")

client = openai.OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1",
)

def safe_history(h):
    s = []
    for e in h:
        d = {'role': e['role']}
        if 'content' in e: d['content'] = e['content']
        if 'tool_calls' in e:
            d['tool_calls'] = [{
                "id": tc["id"],
                "type": tc.get("type", "function"),
                "function": {"name": tc["function"]["name"], "arguments": tc["function"]["arguments"]}
            } for tc in e['tool_calls']]
        if 'tool_call_id' in e:
            d.update({'tool_call_id': e['tool_call_id'], 'name': e['name'], 'content': e['content']})
        s.append(d)
    return s

def handle_tool_calls(msg, history, tools):
    cur = msg
    while getattr(cur, "tool_calls", None):
        tc = cur.tool_calls[0]
        name = tc.function.name
        args = json.loads(tc.function.arguments)
        if name not in tool_registry:
            return f"❌ Tool '{name}' not available."
        res = tool_registry[name](**args)
        history.append({
            "role": "assistant", "content": None,
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)}
            }]
        })
        history.append({"role": "tool", "tool_call_id": tc.id, "name": name, "content": str(res)})
        resp = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "system", "content": system_prompt}] + history,
            tools=tools,
            tool_choice="auto"
        )
        cur = resp.choices[0].message
    return cur.content or "🤖 I couldn't produce a response."

def generate_response(query, save_res=True):
    ensure_save_directory(save_res_location)
    tools = get_available_tools()
    history = load_chat_history()
    history.append({"role": "user", "content": query})
    resp = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[{"role": "system", "content": system_prompt}] + history,
        tools=tools,
        tool_choice="auto"
    )
    msg = resp.choices[0].message
    if getattr(msg, "tool_calls", None):
        final = handle_tool_calls(msg, history, tools)
    else:
        raw = msg.content or "🤖 I couldn't produce a response."
        final = execute_fake_tool_call_if_present(raw)
    history.append({"role": "assistant", "content": final})
    save_chat_history(safe_history(history))
    if save_res:
        with open(save_res_location, "w", encoding="utf-8") as f:
            json.dump({"response": final}, f, ensure_ascii=False, indent=2)
    return final

def stream_response(query):
    tools = get_available_tools()
    history = load_chat_history()
    history.append({"role": "user", "content": query})

    try:
        initial_response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[{"role": "system", "content": system_prompt}] + history,
            tools=tools,
            tool_choice="auto"
        )
        
        msg = initial_response.choices[0].message
        
        if getattr(msg, "tool_calls", None):
            final_response = handle_tool_calls(msg, history, tools)
            final_response = execute_fake_tool_call_if_present(final_response) 
            history.append({"role": "assistant", "content": final_response})
            save_chat_history(safe_history(history))
            yield final_response
            return

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "system", "content": system_prompt}] + history,
            stream=True
        )

        full_response = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                full_response += delta.content
                yield delta.content

        if full_response:
            history.append({"role": "assistant", "content": full_response})
            save_chat_history(safe_history(history))

    except Exception as e:
        print(f"\n[ERROR] Streaming failed: {e}")
