from key_store import KeyStore
from video_queue import VideoQueue
import json
import aiohttp
import asyncio

links = []
with open("./test_links.txt", "r") as file:
    for line in file:
        links.append(line.strip())

def send_links_to_queue():
    video_queue = VideoQueue()

    for link in list(set(links)):
        video_queue.send_message(link)

def get_status():
    keystore = KeyStore()
    print(keystore.get_last_created_id())

async def send_links_to_website():
    async def fetch_data(session, url):
        PARAMS = json.dumps({'link': url})
        async with session.post("http://localhost:8000/api/start_download", data=PARAMS) as response:
            data = response.text
            return data

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in links]
        results = await asyncio.gather(*tasks)

asyncio.run(send_links_to_website())