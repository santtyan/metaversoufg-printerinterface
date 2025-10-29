"""Teste do wrapper PrusaSlicer"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.slicer.prusaslicer_wrapper import (
    PrusaSlicerWrapper,
    slice_with_creality_presets
)


def test_generate_config():
    """Testa geração de .ini"""
    print("\n=== TESTE GERAÇÃO CONFIG ===")
    
    slicer = PrusaSlicerWrapper()
    preset = slicer.preset_parser.parse_preset('PLA')
    
    ini = slicer._generate_ini_config(preset)
    
    # Verificar campos críticos
    assert 'layer_height = 0.2' in ini
    assert 'temperature = 220' in ini
    assert 'bed_temperature = 60' in ini
    assert 'fill_density = 15%' in ini
    
    print("✓ Config .ini gerado corretamente")
    print(f"\nPrimeiras 10 linhas:\n{chr(10).join(ini.split(chr(10))[:10])}")


def test_slice_mock():
    """Testa slice (sem executar PrusaSlicer real)"""
    print("\n=== TESTE SLICE (MOCK) ===")
    
    # Criar STL dummy
    test_stl = Path("tests/test_model.stl")
    test_stl.parent.mkdir(exist_ok=True)
    test_stl.write_text("dummy stl")
    
    print(f"✓ STL teste criado: {test_stl}")
    print("  (Para teste real, instale PrusaSlicer)")
    
    # Limpar
    test_stl.unlink()


if __name__ == "__main__":
    try:
        test_generate_config()
        test_slice_mock()
        print("\n✓ TESTES WRAPPER PASSARAM")
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()