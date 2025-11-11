#!/usr/bin/env python3
"""
Teste do pipeline completo: GLB → STL → Impressão
Verifica se todos os componentes funcionam integrados
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_single_glb(glb_path):
    """Testa conversão e impressão de um único GLB"""
    from src.converters.glb_to_stl import convert_glb_to_stl
    from src.automation.gui_automation import run_gui_workflow
    import yaml
    
    print("="*60)
    print(f"TESTE: {Path(glb_path).name}")
    print("="*60)
    
    # Carregar config
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)
    
    # 1. Converter GLB → STL
    print("\n[1/2] Convertendo GLB → STL...")
    stl_path = convert_glb_to_stl(glb_path)
    
    if not stl_path or not Path(stl_path).exists():
        print("❌ Conversão falhou")
        return False
    
    size_kb = Path(stl_path).stat().st_size / 1024
    print(f"✓ STL gerado: {size_kb:.1f} KB")
    
    # 2. Enviar para impressora via GUI
    print("\n[2/2] Enviando para impressora...")
    preset = "metaverso_PLA.creality_printer"
    
    success = run_gui_workflow(stl_path, preset, cfg)
    
    if success:
        print("\n" + "="*60)
        print("✓ TESTE CONCLUÍDO COM SUCESSO")
        print("="*60)
        return True
    else:
        print("\n❌ Falha na GUI automation")
        return False


def test_all_glbs():
    """Testa todos os GLBs na pasta models/"""
    import yaml
    
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)
    
    models_dir = Path(cfg['paths']['project_root']) / cfg['paths']['models']
    glb_files = list(models_dir.glob("*.glb"))
    
    if not glb_files:
        print(f"❌ Nenhum GLB encontrado em {models_dir}")
        return
    
    print(f"\n🔍 Encontrados {len(glb_files)} GLBs")
    print("="*60)
    
    results = []
    for glb in glb_files:
        print(f"\n>>> Testando: {glb.name}")
        success = test_single_glb(str(glb))
        results.append((glb.name, success))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    for name, success in results:
        status = "✓" if success else "❌"
        print(f"{status} {name}")
    
    total_success = sum(1 for _, s in results if s)
    print(f"\n{total_success}/{len(results)} testes passaram")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Testar GLB específico
        test_single_glb(sys.argv[1])
    else:
        # Testar todos os GLBs
        test_all_glbs()
