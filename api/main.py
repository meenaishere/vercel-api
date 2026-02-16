from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import random
import concurrent.futures

app = FastAPI()

def check_proxy(proxy):
    try:
        # 3 seconds timeout for fast proxies
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get("https://www.google.com", proxies=proxies, timeout=3)
        return proxy if r.status_code == 200 else None
    except:
        return None

@app.get("/")  # Ab aapka main URL hi proxy dega
def get_proxy():
    url = "https://gotoproxy.com/free-proxy-list/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        in_proxies = []
        
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            # Check for Indian proxies (IN)
            if len(cols) > 3 and "IN" in cols[3].text:
                in_proxies.append(f"{cols[0].text.strip()}:{cols[1].text.strip()}")

        if not in_proxies:
            return {"error": "No Indian proxies found on site"}

        # Sirf top 20 check karein fast result ke liye
        working = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(check_proxy, in_proxies[:20])
            working = [res for res in results if res]

        if working:
            return {"proxy": random.choice(working)}
        return {"error": "No working proxy detected right now"}
        
    except Exception as e:
        return {"error": str(e)}
