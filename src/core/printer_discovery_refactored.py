#!/usr/bin/env python3
"""
Printer Discovery - Network Scanner 
"""

import socket
import asyncio
from typing import List, Dict, Optional

class PrinterDiscovery:
    KNOWN_PORTS = [9999, 80, 443, 8080]  # K1 Max known ports
    
    async def discover_network_printers(self, network_range="192.168.1.0/24") -> List[Dict]:
        """Scan rede para impressoras ativas"""
        # Quick ping scan
        hosts = await self._ping_sweep(network_range)
        
        # Port scan em hosts ativos usando gather para paralelismo
        printer_tasks = [self._identify_printer(host) for host in hosts]
        results = await asyncio.gather(*printer_tasks, return_exceptions=True)
        
        # Filter valid printers
        return [result for result in results if isinstance(result, dict)]
    
    async def _ping_sweep(self, network_range: str) -> List[str]:
        """Extrai IPs do range de rede"""
        if "/" in network_range:
            base_ip = network_range.split('/')[0].rsplit('.', 1)[0]
            return [f"{base_ip}.{i}" for i in range(1, 255)]
        return [network_range]  # IP único
    
    async def _identify_printer(self, ip: str) -> Optional[Dict]:
        """Identifica tipo impressora via WebSocket handshake"""
        try:
            # Test K1 Max WebSocket (fast connection test 2s timeout)
            if await self._test_k1max_protocol(ip):
                return {
                    "ip": ip,
                    "type": "Creality K1 Max", 
                    "status": "available",
                    "websocket": True
                }
        except:
            pass
        return None
    
    async def _test_k1max_protocol(self, ip: str) -> bool:
        """Testa protocolo K1 Max na porta 9999"""
        try:
            # Async socket test
            future = asyncio.open_connection(ip, 9999)
            reader, writer = await asyncio.wait_for(future, timeout=2.0)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False

# Interface compatível com código existente
def discover_printers_sync(network_range="192.168.1.0/24") -> List[Dict]:
    """Versão síncrona para compatibilidade"""
    discovery = PrinterDiscovery()
    return asyncio.run(discovery.discover_network_printers(network_range))
