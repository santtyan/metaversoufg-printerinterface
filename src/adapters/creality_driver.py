"""Driver GUI para Creality Print"""
import pyautogui
import subprocess
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CrealityDriver:
    def __init__(self, config):
        self.slicer_path = config['printer']['slicer_path']
        self.preset_file = Path(config['paths']['project_root']) / config['printer']['preset_file']
        self.assets_dir = Path(config['paths']['project_root']) / config['paths']['assets']
        self.startup_delay = config['printer']['startup_delay']
        self.slice_delay = config['printer']['slice_delay']
        self.process = None
    
    def _find_and_click(self, image_name, timeout=30, confidence=0.8):
        """Localiza e clica em imagem"""
        img_path = self.assets_dir / image_name
        start = time.time()
        
        while (time.time() - start) < timeout:
            try:
                loc = pyautogui.locateOnScreen(str(img_path), confidence=confidence)
                if loc:
                    pyautogui.click(pyautogui.center(loc))
                    return True
            except:
                pass
            time.sleep(0.5)
        return False
    
    def start_slicer(self):
        """Inicia Creality Print"""
        try:
            self.process = subprocess.Popen([self.slicer_path])
            time.sleep(self.startup_delay)
            logger.info("Slicer iniciado")
            return True
        except Exception as e:
            logger.error(f"Erro ao iniciar slicer: {e}")
            return False
    
    def import_stl(self, stl_path):
        """Importa arquivo STL"""
        try:
            if not self._find_and_click('open_file_initial_button.png'):
                return False
            time.sleep(1.5)
            
            if not self._find_and_click('file_menu_item.png'):
                return False
            time.sleep(1.5)
            
            if not self._find_and_click('browse_button.png'):
                return False
            time.sleep(2.5)
            
            pyautogui.typewrite(str(stl_path))
            pyautogui.press('enter')
            time.sleep(15)
            
            logger.info("STL importado")
            return True
        except Exception as e:
            logger.error(f"Erro ao importar STL: {e}")
            return False
    
    def apply_preset(self):
        """Aplica preset de material"""
        try:
            if not self._find_and_click('import_config_button.png'):
                return False
            time.sleep(1)
            
            if not self._find_and_click('file_menu_item2.png'):
                return False
            time.sleep(1)
            
            if not self._find_and_click('browse_button.png'):
                return False
            time.sleep(2)
            
            pyautogui.typewrite(str(self.preset_file))
            pyautogui.press('enter')
            time.sleep(3)
            
            pyautogui.press('enter')  # Fallback
            time.sleep(2)
            
            logger.info("Preset aplicado")
            return True
        except Exception as e:
            logger.error(f"Erro ao aplicar preset: {e}")
            return False
    
    def slice_model(self):
        """Fatia modelo"""
        try:
            if self._find_and_click('slice_button.png', timeout=45):
                time.sleep(1)
                pyautogui.click()  # Clique duplo necessário
                time.sleep(self.slice_delay)
            else:
                pyautogui.click(1244, 656)  # Fallback coordenadas
                time.sleep(1)
                pyautogui.click()
                time.sleep(self.slice_delay)
            
            logger.info("Fatiamento concluído")
            return True
        except Exception as e:
            logger.error(f"Erro no fatiamento: {e}")
            return False
    
    def send_to_printer(self):
        """Envia para impressora"""
        try:
            time.sleep(3)
            
            if self._find_and_click('print_send_button.png', timeout=45, confidence=0.75):
                time.sleep(1)
                pyautogui.click()  # Clique adicional
                time.sleep(5)
                logger.info("Enviado para K1 Max")
                return True
            
            logger.error("Botão enviar não encontrado")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar: {e}")
            return False
    
    def cleanup(self):
        """Finaliza processo"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            logger.info("Processo finalizado")