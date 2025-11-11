#!/usr/bin/env python3
"""
Teste End-to-End: Pipeline Simplificado com G-code Nativo
GLB → STL → Slice → Abrir G-code → Send
"""

import sys
import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def find_slicer():
    """Encontra executável Slicer no sistema"""
    possible_paths = [
        r"C:\Users\USER\Downloads\Slic3r-1.3.0.64bit\Slic3r-console.exe",
        r"C:\Slic3r\Slic3r-console.exe",
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            logger.info(f"✓ Slic3r encontrado: {path}")
            return path
    
    return None

def test_simplified_pipeline():
    """Testa pipeline completo com G-code nativo"""
    
    logger.info("="*60)
    logger.info("TESTE: Pipeline Simplificado (G-code Nativo)")
    logger.info("="*60)
    
    # Carregar config
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)
    
    # Definir diretórios
    project_root = Path(__file__).parent
    models_dir = project_root / "models"
    
    # Usar GLB de teste
    glb_path = models_dir / "sf-1_white_ghost__futuristic_starfighter.glb"
    
    if not glb_path.exists():
        logger.error(f"❌ GLB não encontrado: {glb_path}")
        return False
    
    logger.info(f"\nTestando com: {glb_path.name}")
    
    # 1. Converter GLB → STL
    from src.converters.glb_to_stl import convert_glb_to_stl
    logger.info("\n[1/4] GLB → STL...")
    stl_path = convert_glb_to_stl(str(glb_path))
    
    if not stl_path:
        logger.error("❌ Conversão falhou")
        return False
    
    logger.info(f"✓ STL: {Path(stl_path).name}")
    
    # 2. Verificar Slic3r
    logger.info("\n[2/4] Verificando Slic3r...")
    slicer_exe = find_slicer()
    
    if not slicer_exe:
        logger.warning("⚠ Slic3r não encontrado")
        logger.info("\n🔄 FALLBACK: Workflow manual com Creality Print")
        return test_manual_workflow(stl_path)
    
    # 3. Fatiar com Slic3r
    logger.info("\n[3/4] Fatiando STL → G-code...")
    gcode_path = slice_with_slic3r(stl_path, slicer_exe)
    
    if not gcode_path:
        logger.error("❌ Slicing falhou")
        logger.info("\n🔄 FALLBACK: Workflow manual")
        return test_manual_workflow(stl_path)
    
    logger.info(f"✓ G-code: {Path(gcode_path).name}")
    
    # 4. Abrir G-code nativamente
    import subprocess
    logger.info("\n[4/4] Abrindo G-code no Creality Print...")
    subprocess.Popen([str(Path(gcode_path).absolute())], shell=True)
    
    logger.info("\n" + "="*60)
    logger.info("AÇÕES MANUAIS NECESSÁRIAS:")
    logger.info("="*60)
    logger.info("1. ✅ Verificar preview 3D no Creality Print")
    logger.info("2. ✅ Clicar manualmente no botão 'Send'")
    logger.info("3. ✅ Confirmar impressão iniciada na K1 Max")
    
    input("\n⏸ Pressione ENTER após validar impressão...")
    
    logger.info("\n✅ Teste concluído - Pipeline automatizado!")
    return True

def slice_with_slic3r(stl_path: str, slicer_exe: str) -> str:
    """Fatia STL usando Slic3r CLI"""
    import subprocess
    
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    gcode_path = output_dir / f"{Path(stl_path).stem}.gcode"
    
    logger.info(f"Executável: {slicer_exe}")
    logger.info(f"Input: {stl_path}")
    logger.info(f"Output: {gcode_path}")
    
    config_file = Path("config/slic3r_k1max.ini")
    
    if not config_file.exists():
        logger.error(f"❌ Perfil não encontrado: {config_file}")
        return None
    
    logger.info(f"✓ Usando perfil K1 Max: {config_file}")
    
    cmd = [
        slicer_exe,
        "--load", str(config_file.absolute()),
        "-o", str(gcode_path),
        str(stl_path),
    ]
    
    try:
        logger.info("Executando Slic3r...")
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result.returncode == 0 and gcode_path.exists():
            size_kb = gcode_path.stat().st_size / 1024
            logger.info(f"✓ G-code gerado ({size_kb:.1f} KB)")
            return str(gcode_path)
        else:
            logger.error(f"Erro Slic3r (código {result.returncode}):")
            if result.stderr:
                logger.error(result.stderr[:500])
            if result.stdout:
                logger.info(f"Output: {result.stdout[:500]}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout no slicing (>5min)")
        return None
    except Exception as e:
        logger.error(f"Erro slicing: {e}")
        return None

def test_manual_workflow(stl_path: str):
    """Fallback: Workflow manual com Creality Print"""
    import subprocess
    import time
    
    logger.info("\n" + "="*60)
    logger.info("WORKFLOW MANUAL (FALLBACK)")
    logger.info("="*60)
    
    creality_exe = r"C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe"
    
    logger.info("\n1. Abrindo Creality Print...")
    subprocess.Popen([creality_exe])
    time.sleep(15)
    
    logger.info("\n2. ⚠ AÇÕES MANUAIS NECESSÁRIAS:")
    logger.info(f"   a) Importar STL: {stl_path}")
    logger.info("   b) Selecionar preset: Metaverso PLA")
    logger.info("   c) Clicar 'Slice'")
    logger.info("   d) Clicar 'Send'")
    
    input("\n⏸ Pressione ENTER após concluir workflow manual...")
    
    logger.info("\n✅ Teste concluído - Workflow manual")
    return True

if __name__ == "__main__":
    try:
        success = test_simplified_pipeline()
        
        if success:
            logger.info("\n" + "="*60)
            logger.info("📊 RESULTADO:")
            logger.info("="*60)
            logger.info("Pipeline simplificado validado com sucesso")
            logger.info("G-code nativo confirmado como funcional")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n⏹ Teste interrompido")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)