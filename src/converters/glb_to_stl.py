"""Conversor GLB->STL usando Trimesh"""

import logging
from pathlib import Path
import trimesh

logger = logging.getLogger(__name__)

def convert_glb_to_stl(glb_path: str) -> str:
    """Converte GLB para STL"""
    try:
        logger.info(f"Convertendo GLB->STL: {Path(glb_path).name}")
        scene = trimesh.load(glb_path)
        
        if isinstance(scene, trimesh.Scene):
            logger.info(f"GLB contem {len(scene.geometry)} objetos")
            mesh = trimesh.util.concatenate([
                geom for geom in scene.geometry.values()
            ])
        else:
            mesh = scene
        
        stl_path = str(glb_path).replace(".glb", ".stl")
        mesh.export(stl_path)
        
        if Path(stl_path).exists():
            size_kb = Path(stl_path).stat().st_size / 1024
            logger.info(f"STL gerado: {Path(stl_path).name} ({size_kb:.1f} KB)")
            return stl_path
        else:
            logger.error("Falha ao exportar STL")
            return None
            
    except Exception as e:
        logger.error(f"Erro na conversao: {e}")
        return None
