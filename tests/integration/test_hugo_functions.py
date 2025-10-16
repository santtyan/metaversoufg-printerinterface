# test_hugo_functions.py
import asyncio
import websockets
import json
import yaml

async def test_functions():
    # Carregar config
    with open('config/config.yaml') as f:
        cfg = yaml.safe_load(f)
    
    ip = cfg['printer']['ip']
    port = cfg['printer']['websocket_port']
    uri = f"ws://{ip}:{port}"
    
    try:
        # CORREÇÃO: remover timeout do connect()
        async with websockets.connect(uri, ping_interval=None) as ws:
            print(f"✓ Conectado à K1 Max ({ip})\n")
            
            # Aguardar primeira mensagem
            msg = await asyncio.wait_for(ws.recv(), timeout=10)
            status = json.loads(msg)
            
            # Teste is_printing()
            is_printing = status.get('state') in [1, 4] or status.get('printProgress', 0) > 0
            print(f"✓ is_printing() → {is_printing}")
            
            # Teste is_ready()
            is_ready = (
                status.get('state') == 0 and 
                status.get('printProgress', 100) == 0
            )
            print(f"✓ is_ready() → {is_ready}")
            
            # Teste get_material()
            filename = status.get('printFileName', '')
            material = 'UNKNOWN'
            for mat in ['PLA', 'PETG', 'ABS', 'TPU']:
                if mat in filename.upper():
                    material = mat
                    break
            print(f"✓ get_material() → {material}")
            
            print(f"\n📊 Status Completo:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
    except asyncio.TimeoutError:
        print("✗ Timeout aguardando mensagem")
    except Exception as e:
        print(f"✗ Erro: {e}")

asyncio.run(test_functions())