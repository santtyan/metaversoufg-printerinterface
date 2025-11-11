#!/usr/bin/env python3
"""PrusaSlicer CLI wrapper"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class PrusaSlicerWrapper:
    """Wrapper para PrusaSlicer CLI"""
    
    def __init__(self):
        self.exe_paths = [
            r"C:\Program Files\PrusaSlicer\prusa-slicer-console.exe",
            r"C:\ProgramData\chocolatey\bin\prusa-slicer.exe"
        ]
        self.exe_path = self._find_executable()
    
    def _find_executable(self) -> str:
        """Localiza PrusaSlicer no sistema"""
        for path in self.exe_paths:
            if Path(path).exists():
                return path
        raise FileNotFoundError(
            "PrusaSlicer não encontrado. Instale: choco install prusaslicer"
        )
    
    def slice_stl(self, stl_path: str, output_dir: str = "data/output") -> Optional[str]:
        """Fatia STL para G-code otimizado K1 Max"""
        stl_file = Path(stl_path)
        if not stl_file.exists():
            logger.error(f"STL não encontrado: {stl_path}")
            return None
        
        # Setup output
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        gcode_file = output_path / f"{stl_file.stem}.gcode"
        
        logger.info(f"Fatiando: {stl_file.name}")
        
        # PrusaSlicer command com preset K1 Max otimizado
        cmd = [
            self.exe_path, "--slice", str(stl_file),
            "--output", str(gcode_file),
            "--layer-height", "0.2",
            "--nozzle-diameter", "0.4", 
            "--temperature", "220",
            "--bed-temperature", "60",
            "--fill-density", "15%",
            "--support-material"
        ]
        
        return self._execute_slicing(cmd, gcode_file)
    
    def _execute_slicing(self, cmd: list, gcode_file: Path) -> Optional[str]:
        """Executa comando de slicing"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and gcode_file.exists():
                size_kb = gcode_file.stat().st_size / 1024
                logger.info(f"✓ G-code: {gcode_file.name} ({size_kb:.1f} KB)")
                return str(gcode_file)
            
            logger.error(f"Slicing falhou: {result.stderr[:200]}")
            return None
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout no slicing (>5min)")
            return None
        except Exception as e:
            logger.error(f"Erro: {e}")
            return None

# Compatibilidade com interface original
class PrusaSlicer(PrusaSlicerWrapper):
    """Alias para compatibilidade"""
    def __init__(self, config: dict = None):
        super().__init__()

def slice_stl_file(stl_path: str) -> Optional[str]:
    """Função utilitária para slicing rápido"""
    slicer = PrusaSlicerWrapper()
    return slicer.slice_stl(stl_path)