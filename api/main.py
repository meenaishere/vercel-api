from fastapi import FastAPI
import requests
import random
import concurrent.futures
import re

app = FastAPI()

# Indian & Specific Proxy Sources
SOURCES = [
    "https://spys.one/free-proxy-list/IN/",
    "https://free.geonix.com/en/socks4/",
    "https://www.freeproxy.world/?country=IN",
    "https://proxy5.net/free-proxy/india",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=IN&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http&country=IN",
    "https://proxyspace.pro/http.txt",
    "https://raw.githubusercontent.com/Zaeem20/free-proxy-list/master/http.txt" # Indian Focus Repo
]

def check_proxy(proxy):
    """Proxy Testing Logic"""
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        # Google India par check karenge quality confirm karne ke liye
        r = requests.get("https://www.google.co.in", proxies=proxies, timeout=5)
        if r.status_code == 200:
            return proxy
    except:
        return None

@app.get("/")
def get_proxy():
    raw_list = []
    
    # 1. Fetching from all specified sources
    for url in SOURCES:
        try:
            # Browser-like headers takki sites block na karein
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                # Regex se IP:Port nikalna
                ips = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', r.text)
                raw_list.extend(ips)
        except:
            continue

    if not raw_list:
        return {"error": "Sources se koi IP nahi mili. Refresh karein."}

    # Duplicate hatayein
    raw_list = list(set(raw_list))
    random.shuffle(raw_list)

    # 2. Parallel Detection (Filtering)
    working = []
    # 100 proxies test karenge taaki ek na ek working mil jaye
    test_pool = raw_list[:100]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=35) as executor:
        results = executor.map(check_proxy, test_pool)
        working = [res for res in results if res]

    # 3. Final Response
    if working:
        return {
            "status": "success",
            "proxy": random.choice(working),
            "found_indian": len(raw_list),
            "working_now": len(working)
        }
    
    return {
        "error": "Proxies mili hain par koi Indian working proxy nahi mili.",
        "total_found": len(raw_list)
    }
