import asyncio
import aiohttp
import hashlib
import json
import os
import difflib
from bs4 import BeautifulSoup
from datetime import datetime

HASH_FILE = "url_hashes.json"
STATUS_FILE = "status.json"
CONTENT_FILE = "content_store.json"
# URL_FILE = "urls.txt"
URL_FILE = r"C:\Users\Shivam\Desktop\Office\Crawling_project\For_Run\urls.txt"

CONCURRENT_REQUESTS = 50
REQUEST_TIMEOUT = 30

# Load old data
old_hashes = {}
old_content = {}

if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        old_hashes = json.load(f)

if os.path.exists(CONTENT_FILE):
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        old_content = json.load(f)

new_hashes = {}
new_content = {}

async def fetch(session, url):
    try:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            text = await response.text()
            return url, text, None
    except Exception as e:
        return url, None, str(e)

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def generate_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

async def main():
    url_source_map = {}

    with open(URL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                source_id, url = line.strip().split(",", 1)
                url_source_map[url] = source_id

    urls = list(url_source_map.keys())

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    source_status = {}

    for url, html, error in results:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        source_id = url_source_map[url]

        if source_id not in source_status:
            source_status[source_id] = {
                "overall_status": "No Change",
                "last_checked": now,
                "urls": []
            }

        if error:
            url_status = "Error"
            diff = error
            source_status[source_id]["overall_status"] = "Changed"
        else:
            content = extract_text(html)
            new_content[url] = content
            new_hash = generate_hash(content)
            new_hashes[url] = new_hash

            if url not in old_hashes:
                url_status = "New"
                diff = ""
                source_status[source_id]["overall_status"] = "Changed"
            elif old_hashes[url] != new_hash:
                url_status = "Changed"
                old_text = old_content.get(url, "")
                diff = "\n".join(difflib.unified_diff(
                    old_text.splitlines(),
                    content.splitlines(),
                    lineterm=""
                ))
                source_status[source_id]["overall_status"] = "Changed"
            else:
                url_status = "No Change"
                diff = ""

        source_status[source_id]["urls"].append({
            "url": url,
            "status": url_status,
            "diff": diff
        })

    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(new_hashes, f, indent=2)

    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(new_content, f, indent=2)

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(source_status, f, indent=2)

    print("Monitoring Completed")

def run_monitor():
    asyncio.run(main())

if __name__ == "__main__":
    run_monitor()