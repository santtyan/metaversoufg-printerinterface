# test_http_discovery.py
import requests

base = "http://192.168.20.175"

endpoints = [
    "/api/files",
    "/api/printer", 
    "/api/upload",
    "/upload",
    "/printer/upload",
    "/printer/gcode",
    "/v1/files",
]

print("=== DISCOVERY HTTP API ===\n")

for ep in endpoints:
    try:
        r = requests.get(f"{base}{ep}", timeout=3)
        print(f"✓ {ep} → {r.status_code}")
        if r.status_code == 200:
            print(f"  {r.text[:150]}...")
    except requests.RequestException as e:
        print(f"✗ {ep} → {type(e).__name__}")

print("\n=== TEST POST UPLOAD ===\n")

# Testar upload (seguro - arquivo vazio)
try:
    files = {'file': ('test.gcode', 'G28\n')}
    r = requests.post(f"{base}/upload", files=files, timeout=5)
    print(f"POST /upload → {r.status_code}")
    print(f"Response: {r.text[:200]}")
except Exception as e:
    print(f"POST /upload → {type(e).__name__}: {e}")