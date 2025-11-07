# src/k1max/k1max_controller.py
"""
K1 Max Controller - Implementa as 5 funÃ§Ãµes
1. is_printing() - checar se estÃ¡ imprimindo
2. is_ready() - checar se estÃ¡ livre
3. set_material() - checa o  material
4. set_temperature() - checa a  temperatura
5. send_print_job() - enviar objeto para impressÃ£o
"""

import sys
import subprocess
from pathlib import Path
from .monitor import K1MaxMonitor

class K1MaxController:
    def __init__(self, config_path="config/config.yaml"):
        import yaml
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        
        ip = cfg['printer']['ip']
        self.monitor = K1MaxMonitor(ip)
        self.project_root = Path(__file__).parent.parent.parent
    
    def is_printing(self):
        """1. Checar se estÃ¡ imprimindo"""
        return self.monitor.is_printing()
    
    def is_ready(self):
        """2. Checar se estÃ¡ livre e pronta"""
        return self.monitor.is_ready()
    
    def set_material(self, material):
        """
        3. Configurar tipo de material
        Material Ã© configurado no preset do Creality Print
        """
        print(f"Material '{material}' configurado no preset")
        return True
    
    def set_temperature(self, nozzle, bed):
        """
        4. Configurar temperatura
        Temperatura Ã© configurada no preset do Creality Print
        """
        if not (180 <= nozzle <= 300):
            raise ValueError(f"Temperatura nozzle invÃ¡lida: {nozzle}")
        if not (0 <= bed <= 110):
            raise ValueError(f"Temperatura bed invÃ¡lida: {bed}")
        
        print(f"Temperatura: {nozzle}Â°C nozzle, {bed}Â°C bed (configurado no preset)")
        return True
    
    def send_print_job(self, file_path):
        """
        5. Enviar objeto para impressÃ£o
        Executa legacy/script.py que faz todo o workflow
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"Arquivo nÃ£o encontrado: {file_path}")
        
        script = self.project_root / "legacy" / "gui_automation.py"
        
        print(f"Enviando '{file.name}' para impressÃ£o...")
        
        result = subprocess.run(
            [sys.executable, str(script), str(file)],
            cwd=str(self.project_root),
            timeout=300
        )
        
        return result.returncode == 0


if __name__ == "__main__":
    controller = K1MaxController()
    
    print("=== TESTE K1 MAX CONTROLLER ===\n")
    
    print("1. is_printing():", controller.is_printing())
    print("2. is_ready():", controller.is_ready())
    print("3. set_material('PLA'):", controller.set_material("PLA"))
    print("4. set_temperature(210, 60):", controller.set_temperature(210, 60))
    print("\n5. send_print_job() - executar manualmente com arquivo real")


