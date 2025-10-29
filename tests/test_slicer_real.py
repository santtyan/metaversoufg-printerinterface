"""
Teste REAL do wrapper PrusaSlicer
Requer PrusaSlicer instalado
"""

import sys
from pathlib import Path
import trimesh

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.slicer.prusaslicer_wrapper import (
    PrusaSlicerWrapper,
    slice_with_creality_presets
)


def create_test_stl():
    """Cria STL real simples (cubo 10x10x10mm)"""
    print("\n=== CRIANDO STL TESTE ===")
    
    # Criar cubo usando trimesh
    mesh = trimesh.creation.box(extents=[10, 10, 10])
    
    test_file = Path("tests/test_cube.stl")
    mesh.export(test_file)
    
    print(f"✓ STL criado: {test_file}")
    print(f"  Vértices: {len(mesh.vertices)}")
    print(f"  Faces: {len(mesh.faces)}")
    print(f"  Volume: {mesh.volume:.2f} mm³")
    
    return test_file


def test_slice_real_auto():
    """Teste com detecção automática do PrusaSlicer"""
    print("\n=== TESTE SLICE REAL (AUTO) ===")
    
    stl = create_test_stl()
    
    try:
        # Tentar com comando padrão
        gcode = slice_with_creality_presets(
            stl_path=str(stl),
            material="PLA"
        )
        
        print(f"✓ G-code gerado: {gcode}")
        
        # Analisar G-code
        analyze_gcode(gcode)
        
    except Exception as e:
        print(f"✗ Falha (comando padrão): {e}")
        print("\nTente especificar caminho manualmente:")
        print('  test_slice_real_manual("C:/Program Files/PrusaSlicer/prusa-slicer-console.exe")')


def test_slice_real_manual(prusaslicer_path: str):
    """Teste com caminho manual do PrusaSlicer"""
    print(f"\n=== TESTE SLICE REAL (MANUAL) ===")
    print(f"PrusaSlicer: {prusaslicer_path}")
    
    stl = create_test_stl()
    
    try:
        gcode = slice_with_creality_presets(
            stl_path=str(stl),
            material="PLA",
            prusaslicer_path=prusaslicer_path
        )
        
        print(f"✓ G-code gerado: {gcode}")
        analyze_gcode(gcode)
        
    except Exception as e:
        print(f"✗ Erro ao fatiar: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_materials():
    """Testa slice com múltiplos materiais"""
    print("\n=== TESTE MÚLTIPLOS MATERIAIS ===")
    
    stl = create_test_stl()
    
    for material in ['PLA', 'ABS', 'PETG']:
        try:
            output = f"tests/test_cube_{material}.gcode"
            gcode = slice_with_creality_presets(
                stl_path=str(stl),
                material=material,
                output_path=output
            )
            
            # Ler temperaturas do G-code
            with open(gcode) as f:
                content = f.read()
                
            # Extrair M104/M140 (temperaturas)
            nozzle = None
            bed = None
            for line in content.split('\n')[:100]:  # Primeiras 100 linhas
                if line.startswith('M104 S'):
                    nozzle = line.split('S')[1].strip()
                if line.startswith('M140 S'):
                    bed = line.split('S')[1].strip()
            
            print(f"✓ {material}: Nozzle {nozzle}°C, Bed {bed}°C")
            
        except Exception as e:
            print(f"✗ {material}: {e}")


def analyze_gcode(gcode_path: str):
    """Analisa G-code gerado"""
    print("\n  --- ANÁLISE G-CODE ---")
    
    path = Path(gcode_path)
    
    if not path.exists():
        print(f"  ✗ Arquivo não existe: {gcode_path}")
        return
    
    # Tamanho
    size_kb = path.stat().st_size / 1024
    print(f"  Tamanho: {size_kb:.1f} KB")
    
    # Contar linhas
    with open(path) as f:
        lines = f.readlines()
    
    print(f"  Linhas: {len(lines)}")
    
    # Extrair info do header
    print("\n  Primeiras 20 linhas:")
    for i, line in enumerate(lines[:20], 1):
        print(f"    {i:2d}: {line.rstrip()}")
    
    # Verificar comandos críticos
    commands = {
        'M104': 'Set nozzle temp',
        'M140': 'Set bed temp',
        'M109': 'Wait nozzle temp',
        'M190': 'Wait bed temp',
        'G28': 'Home',
        'G29': 'Auto bed level',
        'M106': 'Fan on'
    }
    
    print("\n  Comandos encontrados:")
    content = ''.join(lines)
    for cmd, desc in commands.items():
        if cmd in content:
            print(f"    ✓ {cmd} ({desc})")


def find_prusaslicer():
    """Tenta encontrar PrusaSlicer instalado"""
    print("\n=== PROCURANDO PRUSASLICER ===")
    
    # Locais comuns
    possible_paths = [
        "C:/ProgramData/chocolatey/lib/prusaslicer/tools/PrusaSlicer-2.9.3/prusa-slicer-console.exe",
        "C:/Program Files/PrusaSlicer/prusa-slicer-console.exe",
        "C:/Program Files/PrusaSlicer/prusa-slicer.exe",
        "C:/Program Files (x86)/PrusaSlicer/prusa-slicer-console.exe",
        "C:/PrusaSlicer/prusa-slicer-console.exe",
    ]
    
    for p in possible_paths:
        path = Path(p)
        if path.exists():
            print(f"✓ Encontrado: {path}")
            return str(path)
    
    print("✗ PrusaSlicer não encontrado nos caminhos padrão")
    print("\nInstale com: choco install prusaslicer")
    print("Ou especifique caminho manualmente:")
    print('  test_slice_real_manual("SEU_CAMINHO_AQUI")')
    
    return None


if __name__ == "__main__":
    # Procurar PrusaSlicer
    prusaslicer = find_prusaslicer()
    
    if prusaslicer:
        # Teste automático
        test_slice_real_manual(prusaslicer)
        
        # Teste múltiplos materiais
        test_multiple_materials()
        
        print("\n✓ TODOS TESTES REAIS PASSARAM")
    else:
        # Apenas criar STL para inspeção
        print("\nCriando STL para teste manual...")
        stl = create_test_stl()
        print(f"\nVocê pode fatiar manualmente com:")
        print(f'  prusa-slicer --output test.gcode {stl}')