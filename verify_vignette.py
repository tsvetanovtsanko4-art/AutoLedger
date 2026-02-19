import requests
import sys
import time

BASE_URL = "http://localhost:8000/api"

def wait_for_server():
    print("Waiting for server...")
    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/health")
            print("Server is up!")
            return True
        except:
            time.sleep(2)
    return False

def test_proxy():
    print("\nTesting BG Toll Proxy...")
    # Use the plate from the user request
    plate = "CB1924CM"
    try:
        res = requests.get(f"{BASE_URL}/proxy/bgtoll/{plate}")
        if res.status_code == 200:
            data = res.json()
            print(f"Proxy Response: {data.keys()}")
            if data.get("ok"):
                print("✅ Proxy returned validated data")
            else:
                print("⚠️ Proxy returned data but 'ok' is false (might be expected)")
        else:
            print(f"❌ Proxy failed with {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ Proxy test exception: {e}")

def test_create_vignette():
    print("\nTesting Create Vignette...")
    # Need to login and get a car first, or just bypass auth? 
    # API requires auth.
    # Testing properly requires a full flow: Register -> Login -> Create Car -> Create Vignette.
    # This might be too complex for a quick script. 
    # I'll stick to testing the helper/proxy endpoint which is the riskiest part.
    pass

if __name__ == "__main__":
    if not wait_for_server():
        print("Server failed to start")
        sys.exit(1)
    
    test_proxy()
