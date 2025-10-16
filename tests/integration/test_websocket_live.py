# test_websocket_live.py
import asyncio
import websockets
import json
import yaml
from datetime import datetime

async def monitor_printing():
    # Carregar IP do config
    with open('config/config.yaml') as f:
        cfg = yaml.safe_load(f)
    
    ip = cfg['printer']['ip']
    port = cfg['printer']['websocket_port']
    uri = f"ws://{ip}:{port}"
    
    try:
        # CORREÇÃO: remover timeout do connect()
        async with websockets.connect(uri, ping_interval=None) as ws:
            print(f"✓ Conectado à K1 Max ({ip})")
            print("Monitorando impressão ativa...\n")
            
            for i in range(20):
                # Timeout apenas no recv()
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
                data = json.loads(msg)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}]")
                print(f"  State: {data.get('state', 'N/A')}")
                print(f"  Progress: {data.get('printProgress', 0)}%")
                print(f"  Layer: {data.get('layer', 0)}/{data.get('TotalLayer', 0)}")
                print(f"  Nozzle: {data.get('nozzleTemp', 'N/A')}°C")
                print(f"  Bed: {data.get('bedTemp0', 'N/A')}°C")
                print(f"  Filename: {data.get('printFileName', 'N/A')}")
                print("-" * 50)
                
    except asyncio.TimeoutError:
        print("✗ Timeout aguardando mensagem (impressora não está enviando dados)")
    except Exception as e:
        print(f"✗ Erro: {e}")

asyncio.run(monitor_printing())