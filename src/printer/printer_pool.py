#!/usr/bin/env python3
"""
PrinterPool com pipeline simplificado:
GLB → STL → Slice → Abrir G-code → Send (GUI mínima)
"""

import logging
import subprocess
from queue import Queue
from threading import Thread
from pathlib import Path

logger = logging.getLogger(__name__)

class PrinterPool:
    """Gerencia fila de impressão com pipeline otimizado"""
    
    def __init__(self, config: dict):
        self.queue = Queue()
        self.config = config
        self._running = False
    
    def start(self):
        """Inicia worker thread"""
        self._running = True
        Thread(target=self._worker, daemon=True).start()
        logger.info("PrinterPool iniciado (pipeline nativo G-code)")
    
    def submit_job(self, glb_path: Path, preset: str = "PLA_Standard"):
        """Enfileira job. Non-blocking."""
        self.queue.put((glb_path, preset))
        logger.info(f"Job enfileirado: {glb_path.name}")
    
    def _worker(self):
        """Loop de processamento"""
        while self._running:
            glb_path, preset = self.queue.get()
            try:
                self._process_job(glb_path, preset)
            except Exception as e:
                logger.error(f"Falha job {glb_path.name}: {e}")
            finally:
                self.queue.task_done()
    
    def _process_job(self, glb_path: Path, preset: str):
        """
        Pipeline completo: GLB → STL → G-code → Impressão
        """
        logger.info("="*60)
        logger.info(f"PROCESSANDO: {glb_path.name}")
        logger.info("="*60)
        
        # 1. Converter GLB → STL
        from src.converters.glb_to_stl import convert_glb_to_stl
        logger.info("[1/4] Convertendo GLB → STL...")
        stl_path = convert_glb_to_stl(str(glb_path))
        
        if not stl_path:
            raise ValueError("Conversão GLB→STL falhou")
        
        # 2. Fatiar STL → G-code (PrusaSlicer CLI)
        from src.slicer.prusa_slicer_wrapper import PrusaSlicer
        logger.info("[2/4] Fatiando STL → G-code...")
        slicer = PrusaSlicer(self.config)
        gcode_path = slicer.slice_stl(stl_path)
        
        if not gcode_path:
            raise ValueError("Slicing falhou")
        
        # 3. Abrir G-code no Creality Print (nativo)
        logger.info("[3/4] Abrindo G-code no Creality Print...")
        self._open_gcode_native(gcode_path)
        
        # 4. GUI automation mínima: apenas clicar "Send"
        logger.info("[4/4] Enviando para impressora...")
        self._send_to_printer()
        
        logger.info(f"✓ Job concluído: {glb_path.name}")
    
    def _open_gcode_native(self, gcode_path: str):
        """Abre G-code usando associação nativa do Windows"""
        try:
            subprocess.Popen([str(Path(gcode_path).absolute())], shell=True)
            import time
            time.sleep(10)  # Aguardar Creality carregar preview
        except Exception as e:
            raise RuntimeError(f"Falha ao abrir G-code: {e}")
    
    def _send_to_printer(self):
        """
        GUI automation mínima: apenas clicar botão Send
        """
        import pyautogui
        import time
        
        pyautogui.FAILSAFE = True
        
        # Localizar botão "Print/Send"
        btn_path = Path("assets/print_send_button.png")
        
        try:
            location = pyautogui.locateOnScreen(str(btn_path), confidence=0.8)
            if location:
                pyautogui.click(location)
                logger.info("✓ Botão Send clicado")
                time.sleep(2)
            else:
                logger.warning("⚠ Botão Send não encontrado - verificar manualmente")
        except Exception as e:
            logger.error(f"Erro GUI automation: {e}")
            raise