import os
import requests
import asyncio
import aiohttp
import google.generativeai as genai
import trafilatura
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import time

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

def search1api_search(query: str, max_results: int = 6) -> list:
    url = "https://api.search1api.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "query": query,
        "search_service": "google",
        "max_results": max_results,
        "crawl_results": 0,
        "image": False,
        "language": "en",
        "time_range": "year"
    }

    print(f"Searching for: {query}")
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])

def is_scrapable(url: str, user_agent: str = "*") -> bool:
    try:
        parsed = urlparse(url)
        robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")

        print("Checking Robots.txt...")

        response = requests.get(robots_url, timeout=2)
        if response.status_code != 200:
            print(f"No robots.txt or inaccessible: {robots_url}")
            return False

        rp = RobotFileParser()
        rp.parse(response.text.splitlines())
        allowed = rp.can_fetch(user_agent, url)
        print(f"Checked robots.txt: {url} => {'Allowed' if allowed else 'Blocked'}")
        return allowed
    except Exception as e:
        print(f"robots.txt check failed for {url}: {e}")
        return False
    

def filter_scrapable_urls_parallel(urls: list[str]) -> list[str]:
    print("\nChecking robots.txt for scrapable URLs in parallel...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(is_scrapable, urls))
    return [url for url, allowed in zip(urls, results) if allowed]

async def fetch_content(session, url, timeout):
    try:
        print(f"Fetching URL: {url}")
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                html = await response.text()
                result = trafilatura.extract(html, include_comments=False, include_tables=False)
                snippet = result[:500] if result else ""
                print(f"Scraped {len(snippet)} characters")
                return snippet
            else:
                print(f"Non-200 status: {response.status}")
                return ""
    except asyncio.TimeoutError:
        print(f"Timeout scraping: {url}")
        return ""
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

async def parallel_scrape_async(urls: list[str], timeout: int = 3) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_content(session, url, timeout) for url in urls]
        return await asyncio.gather(*tasks)

def summerize(results, query):
    chat = model.start_chat()
    full_text = f"You are a website summarizer. Here's the user query: '{query}'\n\nWeb search results:\n" + \
        "\n\n".join([f"{r['name']}:\n{r['body']}" for r in results])
    response = chat.send_message(full_text)
    if response and response.text:
        print("Summary:", response.text)
        return response.text
    else:
        print("Failed to generate summary.")
        return None

def web_search(query: str) -> list:
    results = []
    
    search_results = search1api_search(query)
    urls = [r["link"] for r in search_results if r.get("link")]

    scrapable_urls = filter_scrapable_urls_parallel(urls)

    # Only scrape first 3 scrapable URLs you can change definately
    scrapable_urls = scrapable_urls[:3]

    print(f"\nSearching first {len(scrapable_urls)} urls\n")
    bodies = asyncio.run(parallel_scrape_async(scrapable_urls))

    for i, (url, body) in enumerate(zip(scrapable_urls, bodies)):
        results.append({
            "name": f"Result {i+1}",
            "url": url,
            "body": body
        })

    summary = summerize(results, query)
    return scrapable_urls if summary is None else summary


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
                }
            },
            "required": ["query"]
        }
    }
}

if __name__ == "__main__":
    start_time = time.time()

    run = web_search("who win this ipl")

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    print("\nFinal Results:")
    if isinstance(run, str):
        print(run)
    else:
        for r in run:
            print(r)

    print(f"\n⏱️ Time taken: {duration} seconds")