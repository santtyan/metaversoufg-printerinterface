import requests

base = "http://192.168.20.175"
gcode = "G28\nM105\nM84\n"  # Comandos seguros

files = {'file': ('test.gcode', gcode)}
r = requests.post(f"{base}/upload", files=files, timeout=10)

print(f"Status: {r.status_code}")
print(f"Response: {r.text}")