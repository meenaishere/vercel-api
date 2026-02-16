from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import random
import concurrent.futures

# Ye line sabse important hai Vercel ke liye
app = FastAPI()

def check_proxy(proxy):
    # Sirf wahi proxy rakhein jo 3 seconds ke andar response de rahi ho
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get("https://www.google.com", proxies=proxies, timeout=3)
        return proxy if r.status_code == 200 else None
    except:
        return None

@app.get("/get-proxy")
def get_random_indian_proxy():
    # 1. Scrape from Gotoproxy
    url = "https://gotoproxy.com/free-proxy-list/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    in_proxies = []
    for row in soup.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 3 and "IN" in cols[3].text:
            in_proxies.append(f"{cols[0].text.strip()}:{cols[1].text.strip()}")

    # 2. Parallel Testing (Detection)
    working = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        results = executor.map(check_proxy, in_proxies[:30]) # Top 30 check karein
        working = [res for res in results if res]

    if working:
        return {"proxy": random.choice(working)} # Ek random working proxy dein
    return {"error": "No working Indian proxy found at the moment"}
