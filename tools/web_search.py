import os
import requests
import asyncio
import google.generativeai as genai
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
import time
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": 1.2,
        "top_p": 0.9,
        "top_k": 50
    },
    system_instruction="You are website summerizer, You will be provided websites raw text and a user query, you have to summarize the whole content from the websites"
)

def serper_search(query: str, max_results: int = 6) -> list[str]:
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "q": query,
        "gl": "in",
        "num": max_results
    })

    print(f"Searching for: {query}")
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    data = response.json()
    links = [item["link"] for item in data.get("organic", []) if "link" in item]
    print(f"✅ Found {len(links)} results")
    return links

async def parallel_scrape_async(urls: list[str], timeout: int = 3) -> list[str]:
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(urls)
        bodies = []
        for res in results:
            if res.success and res.markdown:
                snippet = res.markdown
                bodies.append(snippet)
            else:
                print(f"❌ Failed to scrape: {res.url}")
                bodies.append("")
        return bodies

def summerize(results, query):
    chat = model.start_chat()
    full_text = f"You are a website summarizer. Here's the user query: '{query}'\n\nWeb search results:\n" + \
        "\n\n".join([f"{r['name']}:\n{r['body']}" for r in results])
    response = chat.send_message(full_text)
    if response and response.text:
        print("Summary:", response.text, "\n")
        return response.text
    else:
        print("Failed to generate summary.")
        return None

def web_search(query: str, num: int = 4) -> str | list:
    results = []
    num = min(max(num, 1), 20)

    urls = serper_search(query, max_results=num)

    print(f"\nScraping {len(urls)} URLs\n")
    bodies = asyncio.run(parallel_scrape_async(urls))

    for i, (url, body) in enumerate(zip(urls, bodies)):
        results.append({
            "name": f"Result {i+1}",
            "url": url,
            "body": body
        })

    summary = summerize(results, query)
    return urls if summary is None else summary

tool_definition = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Searches the web for real-time information and returns the scrape websites summary.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on web for real-time information."
                },
                "num": {
                    "type": "integer",
                    "description": "How many websites to scrape (default 4, max 20) it is mandatory to scrape at least 4 urls",
                    "default": 4
                }
            },
            "required": ["query"]
        }
    }
}

if __name__ == "__main__":
    start_time = time.time()

    run = web_search("who won IPL 2025", num=4)

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    print("\nFinal Results:")
    if isinstance(run, str):
        print(run)
    else:
        for r in run:
            print(r)

    print(f"\n⏱️ Time taken: {duration} seconds")
