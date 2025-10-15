# src/k1max/k1max_controller.py
"""
K1 Max Controller - Implementa as 5 funções
1. is_printing() - checar se está imprimindo
2. is_ready() - checar se está livre
3. set_material() - configurar material
4. set_temperature() - configurar temperatura
5. send_print_job() - enviar objeto para impressão
"""

import sys
import subprocess
from pathlib import Path
from .k1max_monitor import K1MaxMonitor

class K1MaxController:
    def __init__(self, config_path="config/config.yaml"):
        import yaml
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        
        ip = cfg['printer']['ip']
        self.monitor = K1MaxMonitor(ip)
        self.project_root = Path(__file__).parent.parent.parent
    
    def is_printing(self):
        """1. Checar se está imprimindo"""
        return self.monitor.is_printing()
    
    def is_ready(self):
        """2. Checar se está livre e pronta"""
        return self.monitor.is_ready()
    
    def set_material(self, material):
        """
        3. Configurar tipo de material
        Material é configurado no preset do Creality Print
        """
        print(f"Material '{material}' configurado no preset")
        return True
    
    def set_temperature(self, nozzle, bed):
        """
        4. Configurar temperatura
        Temperatura é configurada no preset do Creality Print
        """
        if not (180 <= nozzle <= 300):
            raise ValueError(f"Temperatura nozzle inválida: {nozzle}")
        if not (0 <= bed <= 110):
            raise ValueError(f"Temperatura bed inválida: {bed}")
        
        print(f"Temperatura: {nozzle}°C nozzle, {bed}°C bed (configurado no preset)")
        return True
    
    def send_print_job(self, file_path):
        """
        5. Enviar objeto para impressão
        Executa legacy/script.py que faz todo o workflow
        """
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        script = self.project_root / "legacy" / "script.py"
        
        print(f"Enviando '{file.name}' para impressão...")
        
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