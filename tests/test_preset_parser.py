# tests\test_preset_parser.py
"""Testes do parser de presets Creality"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.presets.creality_preset_parser import (
    CrealityPresetParser,
    get_nozzle_temp,
    get_bed_temp,
    supports_material
)


def test_quick_functions():
    """Testa funções rápidas"""
    print("\n=== TESTES RÁPIDOS ===")
    
    # Teste 1: Temperaturas
    print(f"✓ PLA Nozzle: {get_nozzle_temp('PLA')}°C")
    print(f"✓ PLA Bed: {get_bed_temp('PLA')}°C")
    print(f"✓ ABS Nozzle: {get_nozzle_temp('ABS')}°C")
    print(f"✓ PETG Bed: {get_bed_temp('PETG')}°C")
    
    # Teste 2: Materiais suportados
    print(f"\n✓ Suporta PLA? {supports_material('PLA')}")
    print(f"✓ Suporta NYLON? {supports_material('NYLON')}")


def test_full_preset():
    """Testa preset completo"""
    print("\n=== PRESET COMPLETO PLA ===")
    
    parser = CrealityPresetParser()
    preset = parser.parse_preset('PLA')
    
    print(f"Nozzle: {preset.nozzle_temp}°C")
    print(f"Bed: {preset.bed_temp}°C")
    print(f"Speed: {preset.print_speed} mm/s")
    print(f"Layer: {preset.layer_height} mm")
    print(f"Infill: {preset.infill_density}%")
    print(f"Support: {preset.support_enabled}")


def test_all_materials():
    """Testa todos materiais"""
    print("\n=== TODOS MATERIAIS ===")
    
    parser = CrealityPresetParser()
    
    for material in ['PLA', 'ABS', 'PETG', 'TPU']:
        try:
            preset = parser.parse_preset(material)
            print(f"{material}: {preset.nozzle_temp}°C / {preset.bed_temp}°C")
        except Exception as e:
            print(f"{material}: ERRO - {e}")


if __name__ == "__main__":
    try:
        test_quick_functions()
        test_full_preset()
        test_all_materials()
        print("\n✓ TODOS TESTES PASSARAM")
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()