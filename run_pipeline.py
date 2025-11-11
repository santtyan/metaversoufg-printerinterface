#!/usr/bin/env python3
"""
Pipeline Simplificado: GLB → STL → G-code → Send
Entry point principal para execução direta (sem API)

Uso:
    python run_pipeline.py                          # Processa todos GLBs em models/
    python run_pipeline.py model.glb                # Processa GLB específico
    python run_pipeline.py --watch                  # Monitora pasta models/
"""

import sys
import yaml
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def find_slicer():
    """Encontra executável Slic3r no sistema"""
    possible_paths = [
        r"C:\Users\USER\Downloads\Slic3r-1.3.0.64bit\Slic3r-console.exe",
        r"C:\Slic3r\Slic3r-console.exe",
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    return None

def process_glb(glb_path: str) -> bool:
    """
    Processa um GLB através do pipeline completo
    
    Args:
        glb_path: Caminho para arquivo GLB
        
    Returns:
        True se sucesso, False se falha
    """
    from src.converters.glb_to_stl import convert_glb_to_stl
    import subprocess
    
    logger.info("="*60)
    logger.info(f"PROCESSANDO: {Path(glb_path).name}")
    logger.info("="*60)
    
    # 1. Converter GLB → STL
    logger.info("\n[1/3] GLB → STL...")
    stl_path = convert_glb_to_stl(str(glb_path))
    
    if not stl_path:
        logger.error("❌ Conversão falhou")
        return False
    
    logger.info(f"✓ STL: {Path(stl_path).name}")
    
    # 2. Verificar Slic3r
    logger.info("\n[2/3] Verificando Slic3r...")
    slicer_exe = find_slicer()
    
    if not slicer_exe:
        logger.error("❌ Slic3r não encontrado")
        logger.info("Instale: https://dl.slic3r.org/win/Slic3r-1.3.0.64bit.zip")
        return False
    
    logger.info(f"✓ Slic3r: {slicer_exe}")
    
    # 3. Fatiar STL → G-code
    logger.info("\n[3/3] Fatiando STL → G-code...")
    
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    gcode_path = output_dir / f"{Path(stl_path).stem}.gcode"
    
    config_file = Path("config/slic3r_k1max.ini")
    
    if not config_file.exists():
        logger.error(f"❌ Perfil não encontrado: {config_file}")
        return False
    
    cmd = [
        slicer_exe,
        "--load", str(config_file.absolute()),
        "-o", str(gcode_path),
        str(stl_path),
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result.returncode == 0 and gcode_path.exists():
            size_kb = gcode_path.stat().st_size / 1024
            logger.info(f"✓ G-code gerado ({size_kb:.1f} KB)")
            logger.info(f"✓ Salvo em: {gcode_path}")
            
            # Abrir Creality Print automaticamente
            logger.info("\n📂 Abrindo G-code no Creality Print...")
            subprocess.Popen([str(gcode_path.absolute())], shell=True)
            
            logger.info("\n" + "="*60)
            logger.info("✅ PIPELINE CONCLUÍDO")
            logger.info("="*60)
            logger.info("⏭  PRÓXIMO PASSO: Clique 'Enviar impressão' no Creality Print")
            
            return True
        else:
            logger.error(f"❌ Slicing falhou (código {result.returncode})")
            if result.stderr:
                logger.error(result.stderr[:500])
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout no slicing (>5min)")
        return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False

def process_all_glbs():
    """Processa todos GLBs na pasta models/"""
    models_dir = Path("models")
    glb_files = list(models_dir.glob("*.glb"))
    
    if not glb_files:
        logger.warning(f"⚠️  Nenhum GLB encontrado em {models_dir}")
        logger.info("Adicione arquivos .glb na pasta models/ para processar")
        return False
    
    logger.info(f"📦 {len(glb_files)} GLBs detectados")
    
    success_count = 0
    for glb_path in glb_files:
        if process_glb(str(glb_path)):
            success_count += 1
        logger.info("")  # Linha em branco entre processamentos
    
    logger.info("="*60)
    logger.info(f"📊 RESULTADO FINAL: {success_count}/{len(glb_files)} processados com sucesso")
    logger.info("="*60)
    
    return success_count == len(glb_files)

def watch_mode():
    """Monitora pasta models/ por novos GLBs"""
    import time
    
    logger.info("="*60)
    logger.info("👁️  MODO WATCH: Monitorando models/")
    logger.info("="*60)
    logger.info("Pressione Ctrl+C para parar\n")
    
    processed = set()
    models_dir = Path("models")
    
    try:
        while True:
            glb_files = set(models_dir.glob("*.glb"))
            new_files = glb_files - processed
            
            for glb_path in new_files:
                logger.info(f"\n🆕 Novo GLB detectado: {glb_path.name}")
                if process_glb(str(glb_path)):
                    processed.add(glb_path)
            
            time.sleep(5)  # Check every 5s
            
    except KeyboardInterrupt:
        logger.info("\n⏹️  Modo watch interrompido")

def main():
    """Entry point principal"""
    parser = argparse.ArgumentParser(
        description="Pipeline automatizado GLB → G-code para K1 Max"
    )
    parser.add_argument(
        "glb_file", 
        nargs="?", 
        help="Arquivo GLB para processar (opcional)"
    )
    parser.add_argument(
        "--watch", 
        action="store_true",
        help="Monitorar pasta models/ por novos arquivos"
    )
    
    args = parser.parse_args()
    
    try:
        if args.watch:
            watch_mode()
            return True
        elif args.glb_file:
            return process_glb(args.glb_file)
        else:
            return process_all_glbs()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)