"""Conversão GLB para STL"""
import trimesh
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def convert_glb_to_stl(glb_path):
    """Converte GLB para STL"""
    try:
        glb_path = Path(glb_path)
        if not glb_path.exists():
            logger.error(f"GLB não encontrado: {glb_path}")
            return None
        
        stl_path = glb_path.with_suffix('.stl')
        mesh = trimesh.load(str(glb_path))
        mesh.export(str(stl_path))
        
        if stl_path.exists():
            logger.info(f"Conversão concluída: {stl_path.name}")
            return str(stl_path)
        
        return None
    except Exception as e:
        logger.error(f"Erro na conversão: {e}")
        return None