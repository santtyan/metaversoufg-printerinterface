from pathlib import Path
from src.slicer.prusa_slicer_wrapper import slice_with_creality_presets

def test_slice():
    stl_path = "models/charmander(1).stl"
    
    if not Path(stl_path).exists():
        print(f"STL nao encontrado: {stl_path}")
        return
    
    print(f"Fatiando {stl_path} COM PRESET METAVERSO...")
    
    try:
        gcode_path = slice_with_creality_presets(
            stl_path=stl_path,
            material="PLA",
            output_path="models/charmander_metaverso.gcode"
        )
        
        print(f"G-code gerado: {gcode_path}")
        
        if Path(gcode_path).exists():
            size = Path(gcode_path).stat().st_size
            print(f"Tamanho: {size} bytes")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_slice()
