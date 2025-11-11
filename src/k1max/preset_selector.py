# src/printer/preset_selector.py
"""
Lógica de seleção de preset para impressão.
Fallback: 'Metaverso PLA' até schema de metadados ser documentado.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Mapeamento de presets disponíveis
AVAILABLE_PRESETS = {
    "default": "metaverso_PLA.creality_printer",
    "pla": "metaverso_PLA.creality_printer",
    # Expandir quando houver mais presets
}

def choose_preset(obj_metadata: Optional[Dict] = None) -> str:
    """
    Seleciona preset baseado em metadados do objeto.
    
    Args:
        obj_metadata: Metadados do objeto (opcional)
    
    Returns:
        Nome do arquivo de preset (.creality_printer)
    
    Estratégia atual:
        - Sempre retorna preset padrão PLA
        - TODO: Implementar lógica quando schema for documentado
    """
    
    # Por enquanto, sempre usar preset padrão
    preset_name = AVAILABLE_PRESETS["default"]
    
    logger.info(f"Preset selecionado: {preset_name}")
    
    # TODO: Quando metadados estiverem disponíveis, implementar:
    # if obj_metadata:
    #     if obj_metadata.get('material') == 'ABS':
    #         preset_name = AVAILABLE_PRESETS["abs"]
    #     elif obj_metadata.get('detail_level') == 'high':
    #         preset_name = AVAILABLE_PRESETS["high_detail"]
    
    return preset_name


def validate_preset_exists(preset_name: str, assets_dir) -> bool:
    """Verifica se arquivo de preset existe no disco"""
    from pathlib import Path
    preset_path = Path(assets_dir) / preset_name
    exists = preset_path.exists()
    
    if not exists:
        logger.error(f"Preset não encontrado: {preset_path}")
    
    return exists