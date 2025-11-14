"""
Preset Selector - Adaptado para interface coordenador
"""
import logging

logger = logging.getLogger(__name__)

def choosePreset(cfg, obj_glb):
    """
    Escolhe preset baseado em config e metadados do objeto
    """
    preset = cfg['printer']['default_preset']
    logger.info(f"Preset escolhido: {preset}")
    return preset
