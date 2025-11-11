#!/usr/bin/env python3
"""
Pipeline Automatizado: GLB → STL → G-code → K1 Max
Versão refatorada mantendo funcionalidades essenciais

Uso:
    python run_pipeline.py                 # Processa todos GLBs em models/
    python run_pipeline.py arquivo.glb     # Processa GLB específico
    python run_pipeline.py --watch         # Monitora pasta models/
"""

import sys
import logging
import argparse
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class K1MaxPipeline:
    def __init__(self):
        self.slicer_paths = [
            r"C:\Users\USER\Downloads\Slic3r-1.3.0.64bit\Slic3r-console.exe",
            r"C:\Slic3r\Slic3r-console.exe"
        ]
        self.output_dir = Path("data/output")
        self.config_file = Path("config/slic3r_k1max.ini")
    
    def find_slicer(self):
        """Localiza Slic3r no sistema"""
        for path in self.slicer_paths:
            if Path(path).exists():
                return path
        logger.error("❌ Slic3r não encontrado. Instale: https://dl.slic3r.org/win/Slic3r-1.3.0.64bit.zip")
        return None
    
    def process_glb(self, glb_path: str) -> bool:
        """Pipeline completo: GLB → STL → G-code → Creality"""
        from src.converters.glb_to_stl import convert_glb_to_stl
        
        logger.info(f"🔄 Processando: {Path(glb_path).name}")
        
        # 1. GLB → STL
        logger.info("[1/3] Convertendo GLB → STL...")
        stl_path = convert_glb_to_stl(str(glb_path))
        if not stl_path:
            logger.error("❌ Conversão GLB→STL falhou")
            return False
        logger.info(f"✓ STL gerado: {Path(stl_path).name}")
        
        # 2. Verificar Slic3r
        slicer_exe = self.find_slicer()
        if not slicer_exe:
            return False
        
        # 3. STL → G-code
        logger.info("[2/3] Fatiando STL → G-code...")
        if not self._slice_to_gcode(slicer_exe, stl_path):
            return False
        
        # 4. Abrir Creality Print
        logger.info("[3/3] Abrindo Creality Print...")
        gcode_path = self.output_dir / f"{Path(stl_path).stem}.gcode"
        subprocess.Popen([str(gcode_path.absolute())], shell=True)
        
        logger.info("✅ Pipeline concluído! Clique 'Enviar' no Creality Print")
        return True
    
    def _slice_to_gcode(self, slicer_exe: str, stl_path: str) -> bool:
        """Executa slicing STL → G-code"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        gcode_path = self.output_dir / f"{Path(stl_path).stem}.gcode"
        
        if not self.config_file.exists():
            logger.error(f"❌ Perfil não encontrado: {self.config_file}")
            return False
        
        cmd = [slicer_exe, "--load", str(self.config_file), "-o", str(gcode_path), str(stl_path)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and gcode_path.exists():
                size_kb = gcode_path.stat().st_size / 1024
                logger.info(f"✓ G-code gerado ({size_kb:.1f} KB)")
                return True
            else:
                logger.error(f"❌ Slicing falhou (código {result.returncode})")
                if result.stderr:
                    logger.error(result.stderr[:200])
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout no slicing (>5min)")
            return False
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False
    
    def process_all_glbs(self):
        """Processa todos GLBs em models/"""
        glb_files = list(Path("models").glob("*.glb"))
        
        if not glb_files:
            logger.warning("⚠️ Nenhum GLB encontrado em models/")
            return False
        
        logger.info(f"📦 Processando {len(glb_files)} GLBs...")
        success_count = sum(1 for glb in glb_files if self.process_glb(str(glb)))
        
        logger.info(f"📊 Resultado: {success_count}/{len(glb_files)} processados")
        return success_count == len(glb_files)
    
    def watch_mode(self):
        """Monitora models/ por novos GLBs"""
        import time
        
        logger.info("👁️ Modo watch ativo. Ctrl+C para parar")
        processed = set()
        
        try:
            while True:
                new_files = set(Path("models").glob("*.glb")) - processed
                for glb_path in new_files:
                    logger.info(f"🆕 Novo GLB: {glb_path.name}")
                    if self.process_glb(str(glb_path)):
                        processed.add(glb_path)
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info("⏹️ Watch interrompido")

def main():
    """Entry point principal"""
    parser = argparse.ArgumentParser(description="Pipeline GLB → G-code para K1 Max")
    parser.add_argument("glb_file", nargs="?", help="Arquivo GLB específico")
    parser.add_argument("--watch", action="store_true", help="Monitorar pasta models/")
    
    args = parser.parse_args()
    pipeline = K1MaxPipeline()
    
    try:
        if args.watch:
            pipeline.watch_mode()
        elif args.glb_file:
            return pipeline.process_glb(args.glb_file)
        else:
            return pipeline.process_all_glbs()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)