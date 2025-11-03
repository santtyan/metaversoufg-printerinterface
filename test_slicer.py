from pathlib import Path
from src.slicer.prusa_slicer_wrapper import slice_with_creality_presets

stl_path = "models/charmander_fixed.stl"
print(f"Testando {stl_path}...")

try:
    gcode = slice_with_creality_presets(stl_path, "PLA")
    print(f"SUCESSO: {gcode}")
    size = Path(gcode).stat().st_size
    print(f"Tamanho: {size:,} bytes")
except Exception as e:
    print(f"Falhou: {e}")
