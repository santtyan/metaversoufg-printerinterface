"""
Slicer Wrapper - Extração do código Slic3r de run_pipeline.py
"""
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def sliceSTL(cfg, stl_path, preset):
    """
    Fatia STL para G-code usando Slic3r CLI
    
    Args:
        cfg: Configuração (dict do YAML)
        stl_path: Caminho do arquivo STL
        preset: Nome do preset (ex: "PLA")
    
    Returns:
        Caminho do G-code gerado ou None
    """
    slicer_exe = cfg['paths']['slicer_executable']
    slicer_config = cfg['paths']['slicer_config']
    output_dir = Path(cfg['paths']['output'])
    
    if not Path(slicer_exe).exists():
        logger.error(f"✗ Slic3r não encontrado: {slicer_exe}")
        return None
    
    output_dir.mkdir(parents=True, exist_ok=True)
    gcode_path = output_dir / f"{Path(stl_path).stem}.gcode"
    
    cmd = [
        slicer_exe,
        "--load", slicer_config,
        "-o", str(gcode_path),
        str(stl_path)
    ]
    
    try:
        logger.info(f"Fatiando: {Path(stl_path).name}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and gcode_path.exists():
            size_kb = gcode_path.stat().st_size / 1024
            logger.info(f"✓ G-code gerado ({size_kb:.1f} KB)")
            return str(gcode_path)
        else:
            logger.error(f"✗ Slicing falhou (código {result.returncode})")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("✗ Timeout no slicing")
        return None
    except Exception as e:
        logger.error(f"✗ Erro: {e}")
        return None
