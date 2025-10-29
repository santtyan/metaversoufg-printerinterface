#!/usr/bin/env python3
"""Pipeline GLB→STL→G-code→Impressão - Essencial"""

import sys
import time
import logging
import subprocess
from pathlib import Path

try:
    import pyautogui
    import trimesh
except ImportError as e:
    print(f"Módulo ausente: {e}. Execute: pip install pyautogui trimesh")
    sys.exit(1)

# ============= CONFIGURAÇÃO =============
PROJECT_ROOT = Path(r"C:\Projetos\metaversoufg-printerinterface")
SLICER_PATH = r"C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe"
ASSETS_DIR = PROJECT_ROOT / "assets"
MODELS_DIR = PROJECT_ROOT / "models"
PRESET_FILE = ASSETS_DIR / "metaverso_PLA.creality_printer"

SLICER_STARTUP_DELAY = 25
SLICE_PROCESSING_DELAY = 20
DEFAULT_TIMEOUT = 30

# ============= LOGGING =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ============= UTILITÁRIOS =============
def convert_glb_to_stl(glb_path):
    """Converte GLB para STL usando Trimesh"""
    try:
        stl_path = glb_path.replace('.glb', '.stl')
        mesh = trimesh.load(glb_path)
        mesh.export(stl_path)
        logger.info(f"Conversão concluída: {Path(stl_path).name}")
        return stl_path
    except Exception as e:
        logger.error(f"Erro na conversão GLB→STL: {e}")
        return None

def find_and_click(image_name, timeout=DEFAULT_TIMEOUT, confidence=0.9):
    """Localiza imagem na tela e clica no centro"""
    image_path = ASSETS_DIR / image_name
    logger.info(f"Procurando: {image_name}")
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        try:
            location = pyautogui.locateOnScreen(str(image_path), confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                logger.info(f"Clicado em: {image_name}")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    
    logger.error(f"Elemento não encontrado: {image_name}")
    return False

def type_path_and_enter(file_path):
    """Digite caminho e pressiona Enter"""
    logger.info(f"Digitando: {Path(file_path).name}")
    pyautogui.typewrite(str(file_path))
    pyautogui.press('enter')

# ============= PIPELINE =============
def main():
    """Pipeline principal de automação"""
    slicer_process = None
    
    try:
        # 1. Preparar arquivo
        file_path = sys.argv[1] if len(sys.argv) > 1 else MODELS_DIR / "charmander(1).glb"
        
        if str(file_path).endswith('.glb'):
            file_path = convert_glb_to_stl(str(file_path))
            if not file_path:
                return False
        
        # 2. Iniciar slicer
        logger.info("Iniciando slicer...")
        slicer_process = subprocess.Popen([SLICER_PATH])
        time.sleep(SLICER_STARTUP_DELAY)
        
        # 3. Importar STL
        logger.info("Importando arquivo STL...")
        if not find_and_click('open_file_initial_button.png'):
            return False
        time.sleep(1.5)
        
        if not find_and_click('file_menu_item.png'):
            return False
        time.sleep(1.5)
        
        if not find_and_click('browse_button.png'):
            return False
        time.sleep(2.5)
        
        type_path_and_enter(file_path)
        time.sleep(15)
        
        # 4. Importar preset
        logger.info("Importando preset...")
        if not find_and_click('open_file_initial_button.png'):
            return False
        time.sleep(1.5)
        
        if not find_and_click('file_menu_item.png'):
            return False
        time.sleep(1.5)
        
        if not find_and_click('file_menu_item2.png'):
            return False
        time.sleep(1.5)
        
        if not find_and_click('import_config_button.png'):
            return False
        time.sleep(2.5)
        
        type_path_and_enter(PRESET_FILE)
        time.sleep(5)
        
        # Resolver conflitos (com fallback crítico)
        time.sleep(3)
        if find_and_click('criar_copia_button.png', timeout=5, confidence=0.8):
            logger.info("Criou cópia para resolver conflito.")
        time.sleep(2)
        
        if not find_and_click('certo_button.png', timeout=5, confidence=0.8):
            logger.info("Botão 'Certo' não encontrado, pressionando Enter...")
            pyautogui.press('enter')
            time.sleep(2)
        
        logger.info("Configurações importadas.")
        
        # 5. Arranjar e fatiar
        logger.info("Organizando e fatiando...")
        if not find_and_click('arrange_button.png'):
            return False
        time.sleep(5)
        
        # Aguardar interface estabilizar antes de fatiar
        time.sleep(2)
        
        # Fatiar (com clique duplo crítico)
        if find_and_click('slice_button.png', timeout=15, confidence=0.7):
            logger.info("Botão Fatiar encontrado.")
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
            logger.info("Fatiamento iniciado.")
            time.sleep(20)
        else:
            logger.info("Botão Fatiar não encontrado, usando coordenadas fixas...")
            pyautogui.click(1244, 656)
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
            logger.info("Fatiamento iniciado (fallback).")
            time.sleep(20)
        
        logger.info("Fatiamento concluído.")
        
        # 6. Enviar para impressora
        logger.info("Aguardando botão de envio...")
        time.sleep(3)
        
        if find_and_click('print_send_button.png', timeout=45, confidence=0.75):
            logger.info("Botão 'Imprimir/Enviar' encontrado.")
            time.sleep(1)
            pyautogui.click()
            time.sleep(5)
            logger.info("Comando enviado para K1 Max!")
            logger.info("Automação concluída.")
            return True
        
        logger.error("Falha ao encontrar botão 'Imprimir/Enviar'.")
        return False
        
    except Exception as e:
        logger.error(f"Erro no pipeline: {e}")
        return False
    
    finally:
        if slicer_process and slicer_process.poll() is None:
            logger.info("Fechando slicer...")
            slicer_process.terminate()
            time.sleep(5)
            if slicer_process.poll() is None:
                slicer_process.kill()
            logger.info("Slicer fechado.")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)