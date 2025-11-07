#!/usr/bin/env python3
"""Pipeline GLB->STL->Slice->Impressao"""

import sys
import time
import logging
import subprocess
from pathlib import Path

import pyautogui

# Importar do projeto reorganizado
from converters.glb_to_stl import convert_glb_to_stl
from automation.gui_helpers import find_and_click, type_path_and_enter

# Configuracao
PROJECT_ROOT = Path(__file__).parent.parent.parent
SLICER_PATH = r"C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe"
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_INPUT = PROJECT_ROOT / "data" / "input"
DATA_OUTPUT = PROJECT_ROOT / "data" / "output"
PRESET_FILE = ASSETS_DIR / "metaverso_PLA.creality_printer"

SLICER_STARTUP_DELAY = 25
SLICE_PROCESSING_DELAY = 20
DEFAULT_TIMEOUT = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Pipeline principal"""
    slicer_process = None
    
    try:
        logger.info("=" * 60)
        logger.info("PIPELINE: GLB -> STL -> CREALITY -> K1 MAX")
        logger.info("=" * 60)
        
        # 1. Input
        input_file = sys.argv[1] if len(sys.argv) > 1 else DATA_INPUT / "charmander(1).glb"
        input_file = Path(input_file)
        
        if not input_file.exists():
            logger.error(f"Arquivo nao encontrado: {input_file}")
            return False
        
        logger.info(f"Input: {input_file.name}")
        
        # 2. Converter GLB->STL
        if input_file.suffix.lower() == ".glb":
            stl_path = convert_glb_to_stl(str(input_file))
            if not stl_path:
                return False
        else:
            stl_path = str(input_file)
        
        # 3. Iniciar Creality
        logger.info("Iniciando Creality Print...")
        slicer_process = subprocess.Popen([SLICER_PATH])
        time.sleep(SLICER_STARTUP_DELAY)
        
        # 4. Importar STL
        logger.info("Importando STL...")
        if not find_and_click("open_file_initial_button.png", ASSETS_DIR):
            return False
        time.sleep(1.5)
        
        if not find_and_click("file_menu_item.png", ASSETS_DIR):
            return False
        time.sleep(1.5)
        
        if not find_and_click("browse_button.png", ASSETS_DIR):
            return False
        time.sleep(2.5)
        
        type_path_and_enter(stl_path)
        time.sleep(15)
        
        # 5. Importar preset
        logger.info("Importando preset...")
        if not find_and_click("open_file_initial_button.png", ASSETS_DIR):
            return False
        time.sleep(1.5)
        
        if not find_and_click("file_menu_item.png", ASSETS_DIR):
            return False
        time.sleep(1.5)
        
        if not find_and_click("file_menu_item2.png", ASSETS_DIR):
            return False
        time.sleep(1.5)
        
        if not find_and_click("import_config_button.png", ASSETS_DIR):
            return False
        time.sleep(2.5)
        
        type_path_and_enter(PRESET_FILE)
        time.sleep(5)
        
        # Resolver conflitos
        time.sleep(3)
        if find_and_click("criar_copia_button.png", ASSETS_DIR, timeout=5, confidence=0.8):
            logger.info("Criou copia para resolver conflito")
        time.sleep(2)
        
        if not find_and_click("certo_button.png", ASSETS_DIR, timeout=5, confidence=0.8):
            logger.info("Botao Certo nao encontrado, pressionando Enter...")
            pyautogui.press("enter")
            time.sleep(2)
        
        logger.info("Configuracoes importadas")
        
        # 6. Arranjar e fatiar
        logger.info("Organizando e fatiando...")
        if not find_and_click("arrange_button.png", ASSETS_DIR):
            return False
        time.sleep(5)
        
        time.sleep(2)
        
        if find_and_click("slice_button.png", ASSETS_DIR, timeout=15, confidence=0.7):
            logger.info("Botao Fatiar encontrado")
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
            logger.info("Fatiamento iniciado")
            time.sleep(SLICE_PROCESSING_DELAY)
        else:
            logger.info("Botao Fatiar nao encontrado, usando coordenadas fixas...")
            pyautogui.click(1244, 656)
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
            logger.info("Fatiamento iniciado (fallback)")
            time.sleep(SLICE_PROCESSING_DELAY)
        
        logger.info("Fatiamento concluido")
        
        # 7. Enviar para impressora
        logger.info("Aguardando botao de envio...")
        time.sleep(3)
        
        if find_and_click("print_send_button.png", ASSETS_DIR, timeout=45, confidence=0.75):
            logger.info("Botao Enviar encontrado")
            time.sleep(1)
            pyautogui.click()
            time.sleep(5)
            
            logger.info("=" * 60)
            logger.info("PIPELINE CONCLUIDO COM SUCESSO")
            logger.info("=" * 60)
            return True
        
        logger.error("Botao Enviar nao encontrado")
        return False
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if slicer_process and slicer_process.poll() is None:
            logger.info("Fechando Creality Print...")
            slicer_process.terminate()
            time.sleep(5)
            if slicer_process.poll() is None:
                slicer_process.kill()

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

