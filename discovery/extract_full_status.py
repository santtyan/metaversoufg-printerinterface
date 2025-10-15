import asyncio
import websockets
import json
from pathlib import Path

async def get_full_status():
    """Extrai 1505 bytes de status para identificar campos Hugo"""
    
    # Salvar na pasta results/
    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)
    
    try:
        async with websockets.connect(
            "ws://192.168.20.138:9999", 
            ping_interval=None,
            ping_timeout=None
        ) as ws:
            await ws.send('{"ping": "test"}')
            response = await ws.recv()
            data = json.loads(response)
            
            # Salvar JSON completo
            output_file = results_dir / 'k1max_full_status.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ {len(data)} campos descobertos")
            print("\n=== CAMPOS CRÍTICOS HUGO ===")
            
            # Buscar campos para tasks Hugo
            hugo_fields = ['material', 'filament', 'filamentType', 'state', 
                          'printState', 'progress', 'printTime', 'printProgress',
                          'jobState', 'printStatus']
            
            found = []
            not_found = []
            
            for key in hugo_fields:
                if key in data:
                    found.append((key, data[key]))
                else:
                    not_found.append(key)
            
            # Mostrar encontrados
            for key, value in found:
                print(f"✅ {key}: {value}")
            
            # Mostrar não encontrados
            for key in not_found:
                print(f"❌ {key}: NÃO ENCONTRADO")
            
            # Mostrar primeiros 30 campos para análise manual
            print("\n=== PRIMEIROS 30 CAMPOS (análise manual) ===")
            for i, (key, value) in enumerate(list(data.items())[:30]):
                value_str = str(value)[:60]
                print(f"{i+1:2d}. {key:30s}: {value_str}")
            
            print(f"\n✓ Total campos: {len(data)}")
            print(f"✓ Salvo em: results/k1max_full_status.json")
            
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== EXTRAÇÃO STATUS K1 MAX ===\n")
    asyncio.run(get_full_status())