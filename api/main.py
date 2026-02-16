from fastapi import FastAPI
import requests
import random
import concurrent.futures
import re

app = FastAPI()

# DEDICATED INDIAN SOURCES (Inse 100% Indian IPs hi milenge)
INDIAN_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=IN&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http&country=IN",
    "https://www.proxyscan.io/download?type=http&country=in"
]

def check_proxy(proxy):
    """Proxy Testing Logic"""
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        # Telegram aur Leeching ke liye Google check sabse best hai
        # Timeout ko 5 sec kiya hai taaki thodi slow proxies bhi accept ho jayein
        r = requests.get("https://www.google.com", proxies=proxies, timeout=5)
        if r.status_code == 200:
            return proxy
    except:
        return None

@app.get("/")
def get_proxy():
    all_proxies = []
    
    # 1. Indian Sources se data uthana
    for url in INDIAN_SOURCES:
        try:
            # Headers add kiye hain taaki source block na kare
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                # IPs extract karna
                proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', r.text)
                all_proxies.extend(proxies)
        except:
            continue

    if not all_proxies:
        return {"error": "Sources se koi IP nahi mili. Kuch der baad try karein."}

    # Duplicate hatayein aur Shuffle karein
    all_proxies = list(set(all_proxies))
    random.shuffle(all_proxies)

    # 2. Parallel Detection (Filtering)
    working = []
    # Zyada proxies test karenge taaki "No working proxy" error na aaye
    test_pool = all_proxies[:100] 
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(check_proxy, test_pool)
        working = [res for res in results if res]

    # 3. Final Response
    if working:
        return {
            "status": "success",
            "proxy": random.choice(working),
            "total_indian_found": len(all_proxies),
            "working_now": len(working)
        }
    
    return {
        "error": "Proxies mili hain par koi bhi working nahi hai.",
        "total_found": len(all_proxies),
        "suggestion": "Refresh karein ya kuch der baad try karein."
    }
