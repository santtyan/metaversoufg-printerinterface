"""
Gerador de dados de teste
Simula estrutura de dados reais para testar análise
"""
import json
from datetime import datetime, timedelta
import random

def generate_test_data():
    """Gera dados simulados para testar websocket_data_analyzer.py"""
    
    messages = []
    start_time = datetime.now()
    
    commands = [
        {"cmd": "get_status"},
        {"cmd": "get_temperature"},
        {"request": "printer_info"},
        {"action": "get_progress"}
    ]
    
    for i in range(100):
        # Comando enviado
        cmd_time = start_time + timedelta(seconds=i*5)
        cmd = random.choice(commands)
        
        messages.append({
            "timestamp": cmd_time.isoformat(),
            "direction": "sent",
            "raw_data": json.dumps(cmd),
            "parsed_data": cmd
        })
        
        # Resposta simulada
        resp_time = cmd_time + timedelta(milliseconds=random.randint(10, 50))
        
        if cmd.get("cmd") == "get_status":
            resp = {"status": "printing", "progress": random.randint(0, 100)}
        elif cmd.get("cmd") == "get_temperature":
            resp = {"nozzle": random.randint(200, 220), "bed": random.randint(50, 70)}
        else:
            resp = {"result": "ok", "data": "simulated"}
        
        messages.append({
            "timestamp": resp_time.isoformat(),
            "direction": "received",
            "raw_data": json.dumps(resp),
            "parsed_data": resp
        })
    
    # Salva
    data = {"captured_messages": messages}
    with open("k1max_websocket_raw_data.json", 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Gerados {len(messages)} mensagens de teste")
    print("Arquivo: k1max_websocket_raw_data.json")
    print("\nAgora você pode testar:")
    print("python websocket_data_analyzer.py")

if __name__ == "__main__":
    generate_test_data()