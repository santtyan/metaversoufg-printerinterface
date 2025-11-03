from pathlib import Path
from src.slicer.prusa_slicer_wrapper import slice_with_creality_presets
import time

modelos = [
    "models/benchy_test.stl",
    "models/overhang_test.stl",
    "models/torus_test.stl"
]

for modelo in modelos:
    if not Path(modelo).exists():
        print(f"ERRO: {modelo} nao encontrado")
        continue
    
    print(f"\n{'='*50}")
    print(f"Fatiando: {Path(modelo).name}")
    print(f"{'='*50}")
    
    start = time.time()
    
    try:
        gcode = slice_with_creality_presets(modelo, "PLA")
        tempo = time.time() - start
        size = Path(gcode).stat().st_size
        
        print(f"SUCESSO em {tempo:.1f}s")
        print(f"   G-code: {size:,} bytes ({size/1024:.1f} KB)")
        
    except Exception as e:
        tempo = time.time() - start
        print(f"FALHOU em {tempo:.1f}s")
        print(f"   Erro: {str(e)[:100]}")

print(f"\n{'='*50}")
print("Testes concluidos!")
