from fastapi import FastAPI
import requests
import random
import concurrent.futures
import re

app = FastAPI()

# Direct GitHub Sources (TheSpeedX & Monosans) jo Gotoproxy bhi use karta hai
SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt"
]

# Indian IP ranges ko identify karne ke liye basic check (Optional but helpful)
# Note: GitHub raw files mein country filter nahi hota, isliye hum testing par depend karenge
def is_indian_proxy(proxy):
    # Free sources aksar mix proxies dete hain. 
    # Agar aapko specifically Indian hi chahiye toh testing ke waqt 
    # hum target website se confirm kar sakte hain.
    return True 

def check_proxy(proxy):
    """Proxy ko check karne wala function"""
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        # Timeout 3 seconds rakha hai taaki bot fast rahe
        # Google.co.in use karne se Indian proxy confirm hone ke chance badh jate hain
        r = requests.get("https://www.google.co.in", proxies=proxies, timeout=3)
        if r.status_code == 200:
            return proxy
    except:
        return None

@app.get("/")
def get_working_proxy():
    all_proxies = []
    
    # 1. Sabhi GitHub sources se data fetch karna
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Regex se IP:Port extract karna
                found = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', response.text)
                all_proxies.extend(found)
        except:
            continue

    if not all_proxies:
        return {"error": "No proxies found from sources."}

    # Duplicate hatayein aur shuffle karein
    all_proxies = list(set(all_proxies))
    random.shuffle(all_proxies)

    # 2. Testing (Detection Logic)
    # Hum pehli 50 proxies check karenge taaki API fast response de
    working = []
    test_pool = all_proxies[:50]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_proxy, test_pool)
        working = [res for res in results if res]

    # 3. Result Return karna
    if working:
        return {
            "status": "success",
            "proxy": random.choice(working),
            "info": f"Tested {len(test_pool)} proxies, found {len(working)} working."
        }
    
    return {"error": "No working proxy detected at this moment. Please refresh."}
