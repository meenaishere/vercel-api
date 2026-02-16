from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import random
import concurrent.futures

app = FastAPI()

# Asli browser jaise headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def check_proxy(proxy):
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        # Telegram testing ke liye google best hai
        r = requests.get("https://www.google.com", proxies=proxies, timeout=3)
        return proxy if r.status_code == 200 else None
    except:
        return None

@app.get("/")
def get_proxy():
    url = "https://gotoproxy.com/free-proxy-list/"
    
    # Session ka use connection errors ko kam karta hai
    session = requests.Session()
    
    try:
        r = session.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status() # Agar status 200 nahi hai toh error dega
        
        soup = BeautifulSoup(r.text, 'html.parser')
        in_proxies = []
        
        # Table parsing
        rows = soup.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) > 3:
                country_text = cols[3].get_text(strip=True)
                if "IN" in country_text or "India" in country_text:
                    ip = cols[0].get_text(strip=True)
                    port = cols[1].get_text(strip=True)
                    in_proxies.append(f"{ip}:{port}")

        if not in_proxies:
            return {"error": "No Indian proxies found on page. Site layout might have changed."}

        # Parallel checking (Testing)
        working = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Top 25 check karein fast result ke liye
            results = executor.map(check_proxy, in_proxies[:25])
            working = [res for res in results if res]

        if working:
            return {"proxy": random.choice(working)}
        
        return {"error": "Found Indian proxies but none are working right now."}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Issue: {str(e)}. Try refreshing after 1 minute."}
