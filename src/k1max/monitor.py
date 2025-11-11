# src/k1max/k1max_monitor.py
"""
K1 Max Monitor - Funções de Leitura via WebSocket
Implementa: is_printing(), is_ready()
"""

import asyncio
import websockets
import json

class K1MaxMonitor:
    def __init__(self, ip="192.168.20.138"):
        self.ws_uri = f"ws://{ip}:9999"
    
    async def _get_status(self):
        """Conecta WebSocket e recebe status da impressora"""
        async with websockets.connect(self.ws_uri, ping_interval=None) as ws:
            # Aguardar broadcast completo (com campo 'state')
            for _ in range(20):
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(msg)
                if 'state' in data:
                    return data
            raise TimeoutError("Broadcast completo não recebido")
    
    def is_printing(self):
        """Verifica se impressora está imprimindo"""
        status = asyncio.run(self._get_status())
        state = status.get('state', 0)
        progress = status.get('printProgress', 0)
        return state == 1 or (0 < progress < 100)
    
    def is_ready(self):
        """Verifica se impressora está pronta (idle + fria)"""
        status = asyncio.run(self._get_status())
        state = status.get("state", 1)
        progress = status.get('printProgress', 100)
        nozzle = float(status.get("nozzleTemp", "999"))
        return state == 0 and progress in [0, 100] and nozzle < 50


if __name__ == "__main__":
    monitor = K1MaxMonitor()
    print(f"Imprimindo: {monitor.is_printing()}")
    print(f"Pronta: {monitor.is_ready()}")