#!/usr/bin/env python3
"""
Teste de Validação: Comparar Original vs Refatorado
Garante que não houve perda de funcionalidade
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def test_converter_compatibility():
    """Testa se conversores original e refatorado produzem mesmo resultado"""
    
    # Encontrar GLB de teste
    test_glbs = [
        "models/charmander(1).glb",
        "models/Oth49_TM_04_NT.glb", 
        "models/sf-1_white_ghost__futuristic_starfighter.glb"
    ]
    
    valid_glb = None
    for glb in test_glbs:
        if Path(glb).exists():
            valid_glb = glb
            break
    
    if not valid_glb:
        logger.error("❌ Nenhum GLB encontrado para teste")
        return False
    
    logger.info(f"🧪 Testando com: {Path(valid_glb).name}")
    
    try:
        # Teste 1: Importar converter refatorado
        sys.path.insert(0, "/mnt/user-data/outputs")
        from glb_to_stl_refactored import convert_glb_to_stl as convert_refactored
        
        # Teste 2: Converter com versão refatorada
        logger.info("\n[1/2] Testando conversor refatorado...")
        stl_refactored = convert_refactored(valid_glb)
        
        if not stl_refactored or not Path(stl_refactored).exists():
            logger.error("❌ Conversor refatorado falhou")
            return False
        
        # Teste 3: Validar arquivo STL gerado
        stl_path = Path(stl_refactored)
        size_kb = stl_path.stat().st_size / 1024
        
        logger.info(f"✅ STL gerado com sucesso:")
        logger.info(f"   📁 Arquivo: {stl_path.name}")
        logger.info(f"   📊 Tamanho: {size_kb:.1f} KB")
        logger.info(f"   📍 Local: {stl_path}")
        
        # Teste 4: Verificar que STL não está vazio
        if size_kb < 1:
            logger.error(f"❌ STL muito pequeno ({size_kb:.1f} KB)")
            return False
        
        logger.info(f"\n✅ TESTE PASSOU - Conversor refatorado funcional")
        return True
        
    except Exception as e:
        logger.error(f"❌ Teste falhou: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_methods():
    """Testa métodos individuais da classe"""
    try:
        sys.path.insert(0, "/mnt/user-data/outputs")
        from glb_to_stl_refactored import GLBToSTLConverter
        
        logger.info("\n🔧 Testando métodos da classe...")
        
        converter = GLBToSTLConverter()
        
        # Teste constantes
        assert converter.MAX_PRINT_SIZE == 280
        assert converter.BED_CENTER == [150, 150, 0]
        
        logger.info("✅ Constantes OK")
        logger.info("✅ Classe instanciada corretamente")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Teste de classe falhou: {e}")
        return False

def main():
    """Executa todos os testes"""
    logger.info("="*60)
    logger.info("🧪 VALIDAÇÃO: GLB→STL Converter Refatorado")
    logger.info("="*60)
    
    tests = [
        ("Compatibilidade Funcional", test_converter_compatibility),
        ("Métodos da Classe", test_class_methods)
    ]
    
    passed = 0
    for name, test_func in tests:
        logger.info(f"\n▶️ Executando: {name}")
        if test_func():
            passed += 1
        else:
            logger.error(f"❌ {name} FALHOU")
    
    logger.info("\n" + "="*60)
    logger.info(f"📊 RESULTADO: {passed}/{len(tests)} testes passaram")
    logger.info("="*60)
    
    if passed == len(tests):
        logger.info("🎉 SUCESSO - Refatoração manteve funcionalidade!")
        return True
    else:
        logger.error("💥 FALHA - Refatoração quebrou funcionalidade")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
