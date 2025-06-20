import requests
import time
import os
from models.config import image_generation_location

import requests
import time
import os
import re
from models.config import image_generation_location

def slugify(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').lower()

def generate_image(
    image_prompt: str,
    model: str = "flux-schnell",
    aspect_ratio: str = "1:1",
    output_dir: str = image_generation_location,
    open_after_generation: bool = True
) -> str:
    url = "https://www.pixelmuse.studio/api/predictions"
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://www.pixelmuse.studio",
        "referer": "https://www.pixelmuse.studio/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    payload = {
        "prompt": image_prompt,
        "model": model,
        "style": "none",
        "aspect_ratio": aspect_ratio
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=35)
        if response.status_code == 201:
            response_data = response.json()
            image_url_list = response_data.get("output", [])
            if isinstance(image_url_list, list) and image_url_list:
                image_url = image_url_list[0]

                os.makedirs(output_dir, exist_ok=True)
                image_response = requests.get(image_url, timeout=35)
                if image_response.status_code == 200 and image_response.content:
                    filename = f"{slugify(image_prompt)}_{int(time.time())}.jpg"
                    output_path = os.path.join(output_dir, filename)
                    with open(output_path, "wb") as file:
                        file.write(image_response.content)

                    if os.path.exists(output_path):
                        if open_after_generation:
                            open_image(output_path)
                        return output_path
                    else:
                        return "Image was not saved successfully."
                else:
                    return f"Failed to download generated image. Status code: {image_response.status_code}"
            else:
                return "No image URL returned."
        else:
            return f"Image generation failed with status code {response.status_code}."
    except Exception as e:
        return f"Error: {str(e)}"

def open_image(image_path: str):
    if os.path.isfile(image_path):
        try:
            os.startfile(image_path) 
        except Exception as e:
            return f"Error opening image: {str(e)}"
    else:
        return "Image file does not exist."

tool_definition = {
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Generates an image based on a text prompt using Pixelmuse Studio API.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_prompt": {
                    "type": "string",
                    "description": "The text prompt describing the image to generate. It has to be in fully detailed prompt"
                },
                "model": {
                    "type": "string",
                    "description": "The model to use for image generation (default: flux-schnell). Others are 'imagine-3', and 'recraft-v3'."
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio of the generated image (default: 1:1). others are (16:9, 9:16)"
                },
                "open_after_generation": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to open the image after generation (default: True). it is a boolean value, not a string.",
                }
            },
            "required": ["image_prompt"]
        }
    }
}
