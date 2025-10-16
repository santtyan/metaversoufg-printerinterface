"""
Analisador de capturas Wireshark (.pcap)
Complementa análise WebSocket
"""
import pyshark
import json
from pathlib import Path

def analyze_pcap(pcap_file: str):
    """Analisa arquivo .pcap do Wireshark"""
    
    capture = pyshark.FileCapture(
        pcap_file,
        display_filter='tcp.port == 9999 and websocket'
    )
    
    messages = []
    
    for packet in capture:
        if hasattr(packet, 'websocket'):
            try:
                ws_data = {
                    'timestamp': float(packet.sniff_timestamp),
                    'src': packet.ip.src,
                    'dst': packet.ip.dst,
                    'opcode': packet.websocket.opcode,
                    'payload': str(packet.websocket.payload) if hasattr(packet.websocket, 'payload') else None
                }
                messages.append(ws_data)
            except Exception as e:
                print(f"Erro: {e}")
    
    # Salva análise
    output = Path("wireshark_analysis.json")
    with open(output, 'w') as f:
        json.dump(messages, f, indent=2)
    
    print(f"Analisados {len(messages)} mensagens WebSocket")
    print(f"Salvo em: {output}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_pcap(sys.argv[1])
    else:
        print("Uso: python analyze_wireshark.py capture.pcap")