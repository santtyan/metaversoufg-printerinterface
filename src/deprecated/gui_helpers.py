"""Funcoes auxiliares para GUI automation"""

import time
import logging
from pathlib import Path
import pyautogui

logger = logging.getLogger(__name__)

def find_and_click(image_name, assets_dir, timeout=30, confidence=0.9):
    """Localiza imagem na tela e clica"""
    image_path = assets_dir / image_name
    
    if not image_path.exists():
        logger.error(f"Asset nao encontrado: {image_path}")
        return False
    
    logger.info(f"Procurando: {image_name}")
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        try:
            location = pyautogui.locateOnScreen(str(image_path), confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                logger.info(f"Clicado: {image_name}")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    logger.error(f"Nao encontrado: {image_name}")
    return False

def type_path_and_enter(file_path):
    """Digite caminho e pressiona Enter"""
    logger.info(f"Digitando: {Path(file_path).name}")
    pyautogui.typewrite(str(file_path), interval=0.05)
    time.sleep(0.5)
    pyautogui.press("enter")

