from pathlib import Path
from src.slicer.prusa_slicer_wrapper import slice_with_creality_presets

def test_model(stl_filename):
    """Testa fatiamento de um modelo STL"""
    stl_path = f"models/{stl_filename}"
    
    if not Path(stl_path).exists():
        print(f"❌ STL não encontrado: {stl_path}")
        return False
    
    print(f"🔄 Testando: {stl_filename}")
    
    try:
        # Fatiar com PLA
        gcode_path = slice_with_creality_presets(
            stl_path=stl_path,
            material="PLA"
        )
        
        if gcode_path and Path(gcode_path).exists():
            size_kb = Path(gcode_path).stat().st_size / 1024
            print(f"✅ SUCESSO: {Path(gcode_path).name}")
            print(f"   Tamanho: {size_kb:.1f} KB")
            return True
        else:
            print(f"❌ FALHOU: G-code não gerado")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    # SEUS MODELOS STL
    modelos = [
        "obj_1_%e.stl",
        "obj_1_dbz_standing_hero.stl",
        "obj_1_0827e1ce25be78b9c3d8b5ec7ac17512.stl", 
        "obj_1_Double_grip_01.stl",
        "cube.stl",  # Modelo que já funciona (controle)
    ]
    
    print("=== TESTE BATCH DE MODELOS ===\n")
    
    sucessos = 0
    total = len(modelos)
    
    for modelo in modelos:
        if test_model(modelo):
            sucessos += 1
        print()  # Linha em branco
    
    print(f"=== RESULTADO: {sucessos}/{total} sucessos ===")
