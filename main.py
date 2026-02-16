from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import concurrent.futures

app = FastAPI()

TARGET_URL = "https://gotoproxy.com/free-proxy-list/"
TEST_URL = "https://www.google.com"

def check_proxy(proxy):
    """Proxy ko check karne wala function"""
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    try:
        # 3 seconds ka timeout rakha hai takki fast proxies milein
        response = requests.get(TEST_URL, proxies=proxies, timeout=3)
        if response.status_code == 200:
            return proxy
    except:
        return None

@app.get("/get-indian-proxies")
def get_proxies():
    # 1. Scraping logic
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(TARGET_URL, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    found_proxies = []
    # Table rows se data nikalna
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 3:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            country = cols[3].text.strip()
            
            if "IN" in country or "India" in country:
                found_proxies.append(f"{ip}:{port}")

    # 2. Testing Logic (Parallel Checking)
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_proxy, found_proxies)
        for res in results:
            if res:
                working_proxies.append(res)

    return {
        "status": "success",
        "total_found": len(found_proxies),
        "working_count": len(working_proxies),
        "proxies": working_proxies
    }
