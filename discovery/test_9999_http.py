import requests
import json
from pathlib import Path

def test_http_on_9999():
    """Testa se porta 9999 aceita requisições HTTP (além de WebSocket)"""
    
    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)
    
    BASE = "http://192.168.20.138:9999"
    
    # Endpoints para testar (foco tasks Hugo)
    endpoints = [
        # Upload/Envio G-code
        ("/api/files/upload", "POST", {"file": "test.gcode", "data": "G28"}),
        ("/upload", "POST", {"file": "test.gcode"}),
        ("/gcode", "POST", {"gcode": "G28"}),
        ("/api/gcode", "POST", {"gcode": "G28"}),
        
        # Controle impressão
        ("/api/print/start", "POST", {"filename": "test.gcode"}),
        ("/api/print/stop", "POST", {}),
        ("/api/print/pause", "POST", {}),
        
        # Status/Info
        ("/api/printer/status", "GET", None),
        ("/api/status", "GET", None),
        ("/status", "GET", None),
        
        # Material/Temperatura
        ("/api/materials", "GET", None),
        ("/api/temperature", "GET", None),
        ("/api/temperature", "POST", {"nozzle": 210, "bed": 60}),
        
        # Comandos genéricos
        ("/command", "POST", {"cmd": "get_status"}),
        ("/api/command", "POST", {"cmd": "get_status"}),
        ("/api", "GET", None),
        ("/", "GET", None)
    ]
    
    results = []
    success_count = 0
    
    print("=== TESTANDO HTTP NA PORTA 9999 ===")
    print("Objetivo: Descobrir se aceita HTTP para tasks Hugo\n")
    
    for endpoint, method, payload in endpoints:
        url = f"{BASE}{endpoint}"
        
        try:
            if method == "GET":
                r = requests.get(url, timeout=3)
            else:
                r = requests.post(url, json=payload, timeout=3)
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': r.status_code,
                'success': r.status_code == 200,
                'response_length': len(r.text) if r.text else 0
            }
            
            results.append(result)
            
            if r.status_code == 200:
                success_count += 1
                print(f"✅ {method:4s} {endpoint:30s} → {r.status_code}")
                if r.text:
                    print(f"    Response: {r.text[:80]}")
            elif r.status_code == 404:
                print(f"⚠️  {method:4s} {endpoint:30s} → 404 Not Found")
            else:
                print(f"⚠️  {method:4s} {endpoint:30s} → {r.status_code}")
                
        except requests.exceptions.ConnectionError:
            results.append({
                'endpoint': endpoint,
                'method': method,
                'success': False,
                'error': 'Connection refused'
            })
            print(f"❌ {method:4s} {endpoint:30s} → Connection refused")
            
        except requests.exceptions.Timeout:
            results.append({
                'endpoint': endpoint,
                'method': method,
                'success': False,
                'error': 'Timeout'
            })
            print(f"⏱️  {method:4s} {endpoint:30s} → Timeout")
            
        except Exception as e:
            results.append({
                'endpoint': endpoint,
                'method': method,
                'success': False,
                'error': str(e)[:50]
            })
            print(f"❌ {method:4s} {endpoint:30s} → {str(e)[:40]}")
    
    # Salvar resultados
    output_file = results_dir / 'test_9999_http_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    # Resumo e conclusão
    print(f"\n=== RESUMO ===")
    print(f"✓ Endpoints HTTP funcionais: {success_count}/{len(endpoints)}")
    print(f"✓ Salvo em: results/test_9999_http_results.json")
    
    print(f"\n=== CONCLUSÃO PARA HUGO ===")
    if success_count == 0:
        print("❌ Porta 9999 NÃO aceita HTTP")
        print("   → Apenas WebSocket disponível")
        print("   → Tasks Hugo devem usar WebSocket ou GUI")
    elif success_count < 3:
        print("⚠️  Porta 9999 aceita HTTP PARCIALMENTE")
        print(f"   → {success_count} endpoint(s) funcionais")
        print("   → Verificar quais tasks Hugo são viáveis")
    else:
        print("✅ Porta 9999 aceita HTTP!")
        print(f"   → {success_count} endpoint(s) funcionais")
        print("   → Algumas tasks Hugo podem ser via HTTP")

if __name__ == "__main__":
    test_http_on_9999()