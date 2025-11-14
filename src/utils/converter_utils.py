"""
Converter Wrapper - Interface para coordenador
"""
import logging
from converters.glb_to_stl import convert_glb_to_stl as _convert

logger = logging.getLogger(__name__)

def convertGlbtoSTL(cfg, obj_glb, preset):
    """Converte GLB para STL (interface coordenador)"""
    glb_path = obj_glb.get('glb_path')
    
    if not glb_path:
        logger.error("✗ GLB path não fornecido")
        return None
    
    logger.info(f"Convertendo: {glb_path}")
    stl_path = _convert(glb_path)
    
    if stl_path:
        logger.info(f"✓ STL gerado: {stl_path}")
    
    return stl_path
