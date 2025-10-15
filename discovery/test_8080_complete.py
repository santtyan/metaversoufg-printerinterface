import requests
from pathlib import Path

def test_8080():
    """Testa se porta 8080 é gateway HTTP→WebSocket ou apenas câmera"""
    
    BASE = "http://192.168.20.138:8080"
    
    print("=== TESTANDO PORTA 8080 ===\n")
    
    # ========================================
    # TESTE 1: Gateway HTTP→WebSocket
    # ========================================
    print("TESTE 1: Gateway HTTP→WebSocket")
    print("Objetivo: Comandos HTTP convertidos para WebSocket\n")
    
    gateway_endpoints = [
        ("/command", {"cmd": "get_status"}),
        ("/api/command", {"cmd": "get_status"}),
        ("/ws/command", {"cmd": "get_status"}),
        ("/gcode", {"gcode": "G28"}),
        ("/printer/command", {"cmd": "get_status"}),
        ("/api/printer", {"cmd": "get_status"}),
        ("/", {"test": "data"})
    ]
    
    gateway_found = False
    
    for endpoint, payload in gateway_endpoints:
        try:
            r = requests.post(f"{BASE}{endpoint}", json=payload, timeout=3)
            
            if r.status_code == 200:
                print(f"✅ POST {endpoint}")
                print(f"   🎯 GATEWAY HTTP ENCONTRADO!")
                print(f"   Response: {r.text[:100]}")
                gateway_found = True
                break
            elif r.status_code != 404:
                print(f"⚠️  POST {endpoint} → {r.status_code}")
                
        except:
            pass
    
    if not gateway_found:
        print("❌ Nenhum gateway HTTP→WebSocket encontrado\n")
    
    # ========================================
    # TESTE 2: MJPG Camera Stream
    # ========================================
    print("\nTESTE 2: MJPG Camera Stream")
    print("Objetivo: Verificar streaming de câmera\n")
    
    mjpg_endpoints = [
        "/?action=stream",
        "/?action=snapshot",
        "/stream",
        "/snapshot.jpg",
        "/video",
        "/camera",
        "/"
    ]
    
    camera_found = False
    camera_endpoint = None
    
    for endpoint in mjpg_endpoints:
        try:
            r = requests.get(f"{BASE}{endpoint}", timeout=5, stream=True)
            content_type = r.headers.get('Content-Type', '')
            
            if 'image' in content_type or 'video' in content_type or 'multipart' in content_type:
                print(f"✅ GET {endpoint}")
                print(f"   Content-Type: {content_type}")
                camera_found = True
                camera_endpoint = endpoint
                break
                
        except:
            pass
    
    if not camera_found:
        print("⚠️  Stream MJPG não confirmado")
    
    # ========================================
    # CONCLUSÃO
    # ========================================
    print("\n" + "="*50)
    print("=== CONCLUSÃO PARA HUGO ===")
    print("="*50)
    
    if gateway_found and camera_found:
        print("✅ Porta 8080 = Gateway HTTP + Câmera (DUAL)")
        print("   → Usar para comandos HTTP (simplifica tasks)")
        print("   → Usar para monitoramento visual")
    elif gateway_found:
        print("✅ Porta 8080 = Gateway HTTP→WebSocket")
        print("   → DESCOBERTA CRÍTICA!")
        print("   → Todas tasks Hugo podem usar HTTP simples")
        print("   → Evita complexidade WebSocket direto")
    elif camera_found:
        print("⚠️  Porta 8080 = Apenas MJPG-Streamer (câmera)")
        print(f"   → Stream disponível em: {camera_endpoint}")
        print("   → Usar apenas para monitoramento visual")
        print("   → NÃO usar para controle impressora")
    else:
        print("❌ Porta 8080 = Função desconhecida")
        print("   → Classificação Nmap como 'http-proxy' incorreta")
        print("   → Requer investigação adicional")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_8080()