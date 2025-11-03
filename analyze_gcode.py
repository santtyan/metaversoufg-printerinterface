from pathlib import Path
import re

def analyze_gcode(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Estatísticas
    stats = {
        'total_lines': len(lines),
        'move_commands': len([l for l in lines if l.startswith('G0') or l.startswith('G1')]),
        'layer_changes': len([l for l in lines if 'LAYER_CHANGE' in l or 'LAYER:' in l]),
        'temp_commands': len([l for l in lines if l.startswith('M104') or l.startswith('M109')]),
        'has_support': 'support' in content.lower(),
        'has_brim': 'brim' in content.lower(),
    }
    
    # Extrair temperaturas
    temps = re.findall(r'M104 S(\d+)', content)
    bed_temps = re.findall(r'M140 S(\d+)', content)
    
    # Estimativa de tempo (se disponível)
    time_match = re.search(r'estimated printing time.*?(\d+)h (\d+)m', content, re.IGNORECASE)
    
    print(f"\n{'='*60}")
    print(f"ANÁLISE: {Path(filepath).name}")
    print(f"{'='*60}")
    print(f"Total de linhas: {stats['total_lines']:,}")
    print(f"Comandos de movimento: {stats['move_commands']:,}")
    print(f"Mudanças de camada: {stats['layer_changes']}")
    print(f"Temperatura nozzle: {temps[0] if temps else 'N/A'}°C")
    print(f"Temperatura bed: {bed_temps[0] if bed_temps else 'N/A'}°C")
    print(f"Suportes: {'SIM' if stats['has_support'] else 'NÃO'}")
    print(f"Brim: {'SIM' if stats['has_brim'] else 'NÃO'}")
    
    if time_match:
        print(f"Tempo estimado: {time_match.group(1)}h {time_match.group(2)}m")
    
    print(f"\n--- PRIMEIRAS 30 LINHAS ---")
    for i, line in enumerate(lines[:30], 1):
        if line.strip():
            print(f"{i:3d}: {line}")

# Analisar todos
gcodes = [
    "models/benchy_test.gcode",
    "models/overhang_test.gcode", 
    "models/torus_test.gcode"
]

for gcode in gcodes:
    if Path(gcode).exists():
        analyze_gcode(gcode)

print(f"\n{'='*60}")
print("Análise concluída!")
