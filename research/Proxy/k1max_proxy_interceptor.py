"""
Proxy Interceptor para K1 Max
Captura TODO tráfego HTTP/WebSocket entre Creality Print e impressora
"""
from mitmproxy import http, ctx
import json
from datetime import datetime
from pathlib import Path

class K1MaxInterceptor:
    def __init__(self):
        self.captured_data = []
        self.output_dir = Path("proxy_captures")
        self.output_dir.mkdir(exist_ok=True)
        self.printer_ip = "200.137.221.11"  # Ajustar no lab
    
    def request(self, flow: http.HTTPFlow) -> None:
        """Intercepta requisições"""
        if self.printer_ip in flow.request.pretty_host:
            data = {
                "timestamp": datetime.now().isoformat(),
                "type": "request",
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "headers": dict(flow.request.headers),
                "content": flow.request.get_text() if flow.request.content else None
            }
            self.captured_data.append(data)
            ctx.log.info(f"REQUEST: {flow.request.method} {flow.request.path}")
    
    def response(self, flow: http.HTTPFlow) -> None:
        """Intercepta respostas"""
        if self.printer_ip in flow.request.pretty_host:
            data = {
                "timestamp": datetime.now().isoformat(),
                "type": "response",
                "status_code": flow.response.status_code,
                "url": flow.request.pretty_url,
                "headers": dict(flow.response.headers),
                "content": flow.response.get_text() if flow.response.content else None
            }
            self.captured_data.append(data)
            ctx.log.info(f"RESPONSE: {flow.response.status_code}")
    
    def websocket_message(self, flow: http.HTTPFlow) -> None:
        """Intercepta mensagens WebSocket"""
        if hasattr(flow, 'websocket') and self.printer_ip in flow.request.pretty_host:
            for msg in flow.websocket.messages:
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "websocket",
                    "from_client": msg.from_client,
                    "content": msg.content.decode('utf-8', errors='ignore')
                }
                self.captured_data.append(data)
                ctx.log.info(f"WS: {'→' if msg.from_client else '←'} {msg.content[:100]}")
    
    def done(self):
        """Salva dados ao final"""
        output_file = self.output_dir / f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.captured_data, f, indent=2, ensure_ascii=False)
        ctx.log.info(f"Captura salva: {output_file}")

addons = [K1MaxInterceptor()]