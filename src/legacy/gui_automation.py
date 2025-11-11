#!/usr/bin/env python3

import sys
import time
import logging
import subprocess
from pathlib import Path

try:
    import pyautogui
    import trimesh
except ImportError as e:
    print(f"MÃ³dulo ausente: {e}. Execute: pip install pyautogui trimesh")
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

# ============= UTILITÃRIOS =============
def convert_glb_to_stl(glb_path):
    """Converte GLB para STL usando Trimesh"""
    try:
        stl_path = glb_path.replace('.glb', '.stl')
        mesh = trimesh.load(glb_path)
        mesh.export(stl_path)
        logger.info(f"ConversÃ£o concluÃ­da: {Path(stl_path).name}")
        return stl_path
    except Exception as e:
        logger.error(f"Erro na conversÃ£o GLBâ†’STL: {e}")
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
    
    logger.error(f"Elemento nÃ£o encontrado: {image_name}")
    return False

def type_path_and_enter(file_path):
    """Digite caminho e pressiona Enter"""
    logger.info(f"Digitando: {Path(file_path).name}")
    pyautogui.typewrite(str(file_path))
    pyautogui.press('enter')

def try_prusaslicer_cli(stl_path, material="PLA"):
    """Tenta slice via PrusaSlicer CLI - retorna None se falhar"""
    try:
        from src.slicer.prusa_slicer_wrapper import slice_with_creality_presets
        logger.info(f"ðŸš€ Tentando PrusaSlicer CLI: {Path(stl_path).name}")
        start_time = time.time()
        
        gcode_path = slice_with_creality_presets(stl_path, material)
        
        if gcode_path and Path(gcode_path).exists():
            slice_time = time.time() - start_time
            file_size = Path(gcode_path).stat().st_size / 1024
            logger.info(f"âœ… CLI sucesso: {slice_time:.1f}s, {file_size:.0f}KB")
            return gcode_path
    except Exception as e:
        logger.warning(f"PrusaSlicer CLI falhou: {e}")
    
    return None

# ============= PIPELINE =============
def main():
    """Pipeline principal de automaÃ§Ã£o"""
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
        
        # Resolver conflitos (com fallback crÃ­tico)
        time.sleep(3)
        if find_and_click('criar_copia_button.png', timeout=5, confidence=0.8):
            logger.info("Criou cÃ³pia para resolver conflito.")
        time.sleep(2)
        
        if not find_and_click('certo_button.png', timeout=5, confidence=0.8):
            logger.info("BotÃ£o 'Certo' nÃ£o encontrado, pressionando Enter...")
            pyautogui.press('enter')
            time.sleep(2)
        
        logger.info("ConfiguraÃ§Ãµes importadas.")
        
        # 5. Arranjar e fatiar
        logger.info("Organizando e fatiando...")
        if not find_and_click('arrange_button.png'):
            return False
        time.sleep(5)
        
        # Aguardar interface estabilizar antes de fatiar
        time.sleep(2)
        
        # === ÃšNICA MUDANÃ‡A: Tentar CLI antes de GUI ===
        cli_gcode = try_prusaslicer_cli(file_path, "PLA")
        if cli_gcode:
            logger.info("â­ï¸ Pulando slice GUI - usando G-code CLI")
            time.sleep(SLICE_PROCESSING_DELAY)  # Simular tempo GUI
        else:
            # Slice GUI original (sem mudanÃ§as)
            if find_and_click('slice_button.png', timeout=15, confidence=0.7):
                logger.info("BotÃ£o Fatiar encontrado.")
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
                logger.info("Fatiamento iniciado.")
                time.sleep(20)
            else:
                logger.info("BotÃ£o Fatiar nÃ£o encontrado, usando coordenadas fixas...")
                pyautogui.click(1244, 656)
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
                logger.info("Fatiamento iniciado (fallback).")
                time.sleep(20)
        # === FIM DA ÃšNICA MUDANÃ‡A ===
        
        logger.info("Fatiamento concluÃ­do.")
        
        # 6. Enviar para impressora
        logger.info("Aguardando botÃ£o de envio...")
        time.sleep(3)
        
        if find_and_click('print_send_button.png', timeout=45, confidence=0.75):
            logger.info("BotÃ£o 'Imprimir/Enviar' encontrado.")
            time.sleep(1)
            pyautogui.click()
            time.sleep(5)
            logger.info("Comando enviado para K1 Max!")
            logger.info("AutomaÃ§Ã£o concluÃ­da.")
            return True
        
        logger.error("Falha ao encontrar botÃ£o 'Imprimir/Enviar'.")
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

