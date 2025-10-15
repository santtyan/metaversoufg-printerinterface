# test_websocket_filtered.py
import asyncio
import websockets
import json
import yaml
from datetime import datetime

async def monitor_printing():
    with open('config/config.yaml') as f:
        cfg = yaml.safe_load(f)
    
    ip = cfg['printer']['ip']
    port = cfg['printer']['websocket_port']
    uri = f"ws://{ip}:{port}"
    
    try:
        async with websockets.connect(uri, ping_interval=None) as ws:
            print(f"✓ Conectado à K1 Max ({ip})")
            print("Aguardando broadcasts completos...\n")
            
            count = 0
            while count < 5:  # Capturar 5 mensagens completas
                msg = await asyncio.wait_for(ws.recv(), timeout=30)
                data = json.loads(msg)
                
                # FILTRO: Apenas mensagens com 'state'
                if 'state' in data:
                    count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Broadcast #{count}")
                    print(f"  State: {data.get('state')}")
                    print(f"  Progress: {data.get('printProgress', 0)}%")
                    print(f"  Layer: {data.get('layer', 0)}/{data.get('TotalLayer', 0)}")
                    print(f"  Nozzle: {data.get('nozzleTemp', 'N/A')}°C")
                    print(f"  Bed: {data.get('bedTemp0', 'N/A')}°C")
                    
                    filename = data.get('printFileName', '')
                    material = 'UNKNOWN'
                    for mat in ['PLA', 'PETG', 'ABS', 'TPU']:
                        if mat in filename.upper():
                            material = mat
                            break
                    
                    print(f"  Material: {material}")
                    print(f"  Filename: {filename}")
                    print("=" * 60)
                    
    except Exception as e:
        print(f"✗ Erro: {e}")

asyncio.run(monitor_printing())