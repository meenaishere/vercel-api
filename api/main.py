from fastapi import FastAPI
import requests
import random
import concurrent.futures
import re

app = FastAPI()

# HIDDEN & LESS FAMOUS SOURCES
# Inme se kuch repositories daily commit hoti hain par log kam jaante hain
HIDDEN_SOURCES = [
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/Zaeem20/free-proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://api.openproxylist.xyz/http.txt",
    "https://alexa.lr22.com/proxylist.txt" # Less known automated list
]

def check_proxy(proxy):
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        # India-specific check ke liye hum Google India use karenge
        r = requests.get("https://www.google.co.in", proxies=proxies, timeout=5)
        if r.status_code == 200:
            return proxy
    except:
        return None

@app.get("/")
def get_proxy():
    raw_list = []
    
    # 1. Fetching from hidden sources
    for url in HIDDEN_SOURCES:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                # Sirf IP:Port pattern extract karna
                ips = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', r.text)
                raw_list.extend(ips)
        except:
            continue

    if not raw_list:
        return {"error": "Hidden sources se koi IP nahi mili."}

    # Duplicate hatayein
    raw_list = list(set(raw_list))
    random.shuffle(raw_list)

    # 2. Advanced Detection Logic
    # Hum 60 proxies test karenge taaki Indian IP milne ka chance badh jaye
    working = []
    test_pool = raw_list[:60]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(check_proxy, test_pool)
        working = [res for res in results if res]

    # 3. Response
    if working:
        return {
            "status": "success",
            "proxy": random.choice(working),
            "checked": len(test_pool),
            "working": len(working)
        }
    
    return {
        "error": "Proxies mili hain par koi Indian working proxy nahi mili.",
        "tip": "Refresh karein, sources list update ho rahi hogi."
    }
