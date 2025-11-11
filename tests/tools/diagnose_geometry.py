#!/usr/bin/env python3
"""
Diagnóstico: Validação de Geometria STL vs Perfil PrusaSlicer
Verifica se o modelo está posicionado dentro do volume de impressão
"""

import trimesh
from pathlib import Path
import configparser

def diagnose_geometry():
    """Valida posicionamento do STL contra bed_shape do perfil"""
    
    print("="*70)
    print("DIAGNÓSTICO: Geometria STL vs Perfil K1 Max")
    print("="*70)
    
    # Paths
    stl_file = Path("models/sf-1_white_ghost__futuristic_starfighter.stl")
    config_file = Path("config/k1max_profile.ini")
    
    # 1. Analisar STL
    print("\n" + "─"*70)
    print("ANÁLISE DO STL")
    print("─"*70)
    
    if not stl_file.exists():
        print(f"❌ STL não encontrado: {stl_file}")
        return
    
    mesh = trimesh.load(str(stl_file))
    bounds = mesh.bounds  # [[min_x, min_y, min_z], [max_x, max_y, max_z]]
    
    print(f"\nArquivo: {stl_file.name}")
    print(f"Vértices: {len(mesh.vertices):,}")
    print(f"Faces: {len(mesh.faces):,}")
    
    print(f"\nBounding Box (mm):")
    print(f"  X: {bounds[0][0]:.2f} a {bounds[1][0]:.2f} (largura: {bounds[1][0] - bounds[0][0]:.2f}mm)")
    print(f"  Y: {bounds[0][1]:.2f} a {bounds[1][1]:.2f} (profundidade: {bounds[1][1] - bounds[0][1]:.2f}mm)")
    print(f"  Z: {bounds[0][2]:.2f} a {bounds[1][2]:.2f} (altura: {bounds[1][2] - bounds[0][2]:.2f}mm)")
    
    # Centro geométrico
    center = mesh.centroid
    print(f"\nCentro geométrico: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
    
    # 2. Analisar Perfil
    print("\n" + "─"*70)
    print("ANÁLISE DO PERFIL K1 MAX")
    print("─"*70)
    
    if not config_file.exists():
        print(f"❌ Perfil não encontrado: {config_file}")
        return
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Buscar seção printer
    printer_section = None
    for section in config.sections():
        if section.startswith("printer:"):
            printer_section = section
            break
    
    if not printer_section:
        print("❌ Seção [printer:] não encontrada no perfil")
        return
    
    print(f"\nSeção encontrada: [{printer_section}]")
    
    # Extrair parâmetros
    bed_shape = config.get(printer_section, "bed_shape", fallback=None)
    max_height = config.get(printer_section, "max_print_height", fallback=None)
    
    print(f"\nParâmetros do perfil:")
    print(f"  bed_shape: {bed_shape}")
    print(f"  max_print_height: {max_height}")
    
    if not bed_shape:
        print("\n❌ ERRO: bed_shape não definido no perfil")
        return
    
    # Parse bed_shape (formato: "0x0,300x0,300x300,0x300")
    try:
        points = []
        for point_str in bed_shape.split(","):
            x, y = point_str.split("x")
            points.append((float(x), float(y)))
        
        bed_min_x = min(p[0] for p in points)
        bed_max_x = max(p[0] for p in points)
        bed_min_y = min(p[1] for p in points)
        bed_max_y = max(p[1] for p in points)
        
        print(f"\nVolume de impressão definido:")
        print(f"  X: {bed_min_x} a {bed_max_x} mm (largura: {bed_max_x - bed_min_x}mm)")
        print(f"  Y: {bed_min_y} a {bed_max_y} mm (profundidade: {bed_max_y - bed_min_y}mm)")
        print(f"  Z: 0 a {max_height} mm (altura: {max_height}mm)")
        
    except Exception as e:
        print(f"\n❌ Erro ao parsear bed_shape: {e}")
        return
    
    # 3. Validação
    print("\n" + "─"*70)
    print("VALIDAÇÃO: STL vs VOLUME DE IMPRESSÃO")
    print("─"*70)
    
    # Verificar se STL está dentro do volume
    stl_min_x, stl_min_y, stl_min_z = bounds[0]
    stl_max_x, stl_max_y, stl_max_z = bounds[1]
    
    issues = []
    
    # Eixo X
    if stl_min_x < bed_min_x:
        issues.append(f"❌ X mínimo do STL ({stl_min_x:.2f}) < cama ({bed_min_x})")
    if stl_max_x > bed_max_x:
        issues.append(f"❌ X máximo do STL ({stl_max_x:.2f}) > cama ({bed_max_x})")
    
    # Eixo Y
    if stl_min_y < bed_min_y:
        issues.append(f"❌ Y mínimo do STL ({stl_min_y:.2f}) < cama ({bed_min_y})")
    if stl_max_y > bed_max_y:
        issues.append(f"❌ Y máximo do STL ({stl_max_y:.2f}) > cama ({bed_max_y})")
    
    # Eixo Z
    if stl_min_z < 0:
        issues.append(f"❌ Z mínimo do STL ({stl_min_z:.2f}) < 0 (abaixo da mesa)")
    if stl_max_z > float(max_height):
        issues.append(f"❌ Z máximo do STL ({stl_max_z:.2f}) > altura máxima ({max_height})")
    
    if issues:
        print("\n🚨 PROBLEMAS DETECTADOS:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n" + "="*70)
        print("CAUSA RAIZ IDENTIFICADA")
        print("="*70)
        print("\nO STL está CENTRALIZADO EM (0,0,0), mas o perfil define:")
        print(f"  - Mesa começando em ({bed_min_x}, {bed_min_y})")
        print(f"  - Centro da mesa deveria ser: ({(bed_max_x - bed_min_x)/2}, {(bed_max_y - bed_min_y)/2})")
        
        print("\n🔧 SOLUÇÃO:")
        print("O conversor GLB->STL precisa posicionar o modelo no CENTRO DA MESA:")
        print(f"  - Deslocar X: +{(bed_max_x - bed_min_x)/2 - center[0]:.2f}mm")
        print(f"  - Deslocar Y: +{(bed_max_y - bed_min_y)/2 - center[1]:.2f}mm")
        print(f"  - Deslocar Z: +{abs(stl_min_z):.2f}mm (garantir Z mínimo = 0)")
        
    else:
        print("\n✅ STL está DENTRO do volume de impressão")
        print("\nSe PrusaSlicer ainda falha, o problema é:")
        print("  1. Perfil não está sendo carregado corretamente")
        print("  2. Versão do PrusaSlicer incompatível com formato INI")
        print("  3. Bug na instalação Chocolatey")
    
    # 4. Recomendações
    print("\n" + "="*70)
    print("PRÓXIMOS PASSOS")
    print("="*70)
    
    if issues:
        print("\n1. Corrigir posicionamento do STL no conversor")
        print("2. Re-executar pipeline após correção")
    else:
        print("\n1. Exportar configurações do PrusaSlicer manualmente:")
        print("   - Abrir PrusaSlicer GUI")
        print("   - Configurar impressora K1 Max manualmente")
        print("   - File > Export > Export Config Bundle")
        print("   - Salvar em config/k1max_from_gui.ini")
        print("   - Comparar com k1max_profile.ini atual")
        print("\n2. Testar slice manual:")
        print("   - Importar STL no PrusaSlicer GUI")
        print("   - Verificar se modelo aparece FORA da mesa")
        print("   - Se sim: problema é posicionamento STL")
        print("   - Se não: problema é parsing CLI do perfil")

if __name__ == "__main__":
    try:
        diagnose_geometry()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
