import asyncio
import websockets
import json
from pathlib import Path
import time

COMMANDS = [
    # Comandos conhecidos
    {"command": "get_temperature"},
    {"command": "fan_control", "speed": 100},
    {"command": "light_control", "state": True},
    {"command": "home"},
    {"command": "get_printer_info"},
    {"command": "list_files"},
    
    # Comandos Hugo (testar viabilidade)
    {"command": "get_material"},
    {"command": "get_filament"},
    {"command": "get_filament_type"},
    {"command": "start_print"},
    {"command": "stop_print"},
    {"command": "pause_print"},
    {"command": "resume_print"},
    {"command": "send_gcode", "gcode": "G28"},
    {"command": "upload_file"},
    {"command": "upload_gcode"},
    {"command": "get_print_status"},
    {"command": "get_status"},
    {"command": "set_temperature", "nozzle": 210, "bed": 60}
]

async def test_commands():
    """Testa comandos Node-RED conhecidos + comandos Hugo"""
    
    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)
    
    try:
        print("🔌 Conectando WebSocket...")
        async with websockets.connect(
            "ws://192.168.20.138:9999",
            ping_interval=None,
            ping_timeout=None
        ) as ws:
            print("✓ Conectado!\n")
            
            results = []
            success_count = 0
            
            print("=== TESTANDO COMANDOS ===\n")
            
            for i, cmd in enumerate(COMMANDS, 1):
                cmd_name = cmd.get('command', 'unknown')
                
                try:
                    await ws.send(json.dumps(cmd))
                    resp = await asyncio.wait_for(ws.recv(), timeout=2)
                    
                    # Tentar parsear resposta
                    try:
                        resp_json = json.loads(resp)
                        resp_preview = json.dumps(resp_json)[:150]
                    except:
                        resp_preview = resp[:150]
                    
                    results.append({
                        'index': i,
                        'command': cmd,
                        'response': resp_preview,
                        'response_length': len(resp),
                        'success': True,
                        'timestamp': time.time()
                    })
                    
                    success_count += 1
                    print(f"✅ {i:2d}. {cmd_name:30s} ({len(resp)} bytes)")
                    
                except asyncio.TimeoutError:
                    results.append({
                        'index': i,
                        'command': cmd,
                        'success': False,
                        'error': 'Timeout (2s)',
                        'timestamp': time.time()
                    })
                    print(f"⏱️  {i:2d}. {cmd_name:30s} (timeout)")
                    
                except Exception as e:
                    results.append({
                        'index': i,
                        'command': cmd,
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                    print(f"❌ {i:2d}. {cmd_name:30s} ({str(e)[:30]})")
                
                await asyncio.sleep(0.5)  # Delay entre comandos
            
            # Salvar resultados
            output_file = results_dir / 'node_red_results.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Resumo
            print(f"\n=== RESUMO ===")
            print(f"✓ Sucessos: {success_count}/{len(COMMANDS)}")
            print(f"✗ Falhas: {len(COMMANDS) - success_count}/{len(COMMANDS)}")
            print(f"📊 Taxa sucesso: {success_count/len(COMMANDS)*100:.1f}%")
            print(f"\n✓ Salvo em: results/node_red_results.json")
            
    except Exception as e:
        print(f"\n✗ Erro conexão: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== TESTE COMANDOS NODE-RED ===\n")
    asyncio.run(test_commands())