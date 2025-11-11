#!/usr/bin/env python3
"""
Wrapper PrusaSlicer CLI para fatiamento automatizado
Gera G-code pronto para abrir nativamente no Creality Print
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class PrusaSlicer:
    """Interface para PrusaSlicer CLI"""
    
    def __init__(self, config: dict):
        self.exe_path = r"C:\Program Files\PrusaSlicer\prusa-slicer-console.exe"
        self.preset_dir = Path(config['paths']['project_root']) / "assets"
        
        # Verificar instalação
        if not Path(self.exe_path).exists():
            raise FileNotFoundError(
                f"PrusaSlicer não encontrado em {self.exe_path}\n"
                "Instale via: choco install prusaslicer"
            )
    
    def slice_stl(self, stl_path: str, output_dir: str = "data/output") -> Optional[str]:
        """
        Fatia STL usando preset Metaverso PLA
        
        Args:
            stl_path: Caminho do arquivo STL
            output_dir: Pasta de saída para G-code
        
        Returns:
            Caminho do G-code gerado ou None se falhar
        """
        stl_path = Path(stl_path)
        if not stl_path.exists():
            logger.error(f"STL não encontrado: {stl_path}")
            return None
        
        # Caminho de saída
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        gcode_path = output_dir / f"{stl_path.stem}.gcode"
        
        logger.info(f"Fatiando: {stl_path.name}")
        
        # Comando PrusaSlicer
        cmd = [
            self.exe_path,
            "--slice",
            str(stl_path),
            "--output", str(gcode_path),
            # Configurações inline (preset Metaverso PLA)
            "--layer-height", "0.2",
            "--nozzle-diameter", "0.4",
            "--filament-diameter", "1.75",
            "--temperature", "220",  # PLA temperatura Creality
            "--bed-temperature", "60",
            "--infill-speed", "80",
            "--perimeter-speed", "60",
            "--fill-density", "10%",
            "--fill-pattern", "honeycomb",
            "--support-material",
            "--support-material-threshold", "45",
            "--printer-model", "K1 Max"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 min timeout
            )
            
            if result.returncode == 0 and gcode_path.exists():
                size_kb = gcode_path.stat().st_size / 1024
                logger.info(f"✓ G-code gerado: {gcode_path.name} ({size_kb:.1f} KB)")
                return str(gcode_path)
            else:
                logger.error(f"PrusaSlicer falhou:\n{result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout no slicing (>5min)")
            return None
        except Exception as e:
            logger.error(f"Erro no slicing: {e}")
            return None


if __name__ == "__main__":
    # Teste rápido
    import yaml
    
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)
    
    slicer = PrusaSlicer(cfg)
    
    # Testar com STL existente
    test_stl = "data/samples/cube.stl"
    if Path(test_stl).exists():
        gcode = slicer.slice_stl(test_stl)
        if gcode:
            print(f"\n✅ Teste bem-sucedido: {gcode}")
        else:
            print("\n❌ Teste falhou")
    else:
        print(f"⚠ STL de teste não encontrado: {test_stl}")