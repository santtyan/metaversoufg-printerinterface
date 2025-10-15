import json
from collections import defaultdict
from pathlib import Path

def extract_schema():
    """Analisa capture_data_2h.json para gerar schema completo"""
    
    results_dir = Path(__file__).parent.parent / 'results'
    capture_file = results_dir / 'capture_data_2h.json'
    
    if not capture_file.exists():
        print("⚠️  capture_data_2h.json não encontrado")
        print(f"   Esperado em: {capture_file}")
        print("\n   Ações:")
        print("   1. Executar P2 (websocket_analyzer) primeiro")
        print("   2. Copiar capture_data_2h.json para results/")
        return
    
    print(f"📂 Lendo: {capture_file}")
    
    with open(capture_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verificar formato
    if isinstance(data, dict) and 'captured_messages' in data:
        messages = data['captured_messages']
    elif isinstance(data, list):
        messages = data
    else:
        print("✗ Formato de dados não reconhecido")
        return
    
    schema = defaultdict(lambda: {
        'type': None,
        'sample_values': [],
        'read_only': True,
        'update_frequency': 0,
        'unique_values': 0
    })
    
    # Analisar mensagens
    print(f"📊 Analisando {len(messages)} mensagens...")
    
    for msg in messages:
        if isinstance(msg, dict):
            for key, value in msg.items():
                schema[key]['type'] = type(value).__name__
                
                # Guardar até 5 valores únicos
                if len(schema[key]['sample_values']) < 5:
                    if value not in schema[key]['sample_values']:
                        schema[key]['sample_values'].append(value)
                
                schema[key]['update_frequency'] += 1
    
    # Detectar campos modificáveis
    for key in schema:
        unique = len(set(str(v) for v in schema[key]['sample_values']))
        schema[key]['unique_values'] = unique
        schema[key]['read_only'] = unique <= 1
    
    # Salvar schema
    output = {
        'metadata': {
            'total_fields': len(schema),
            'total_messages': len(messages),
            'capture_file': str(capture_file)
        },
        'fields': dict(schema)
    }
    
    output_file = results_dir / 'k1max_protocol_schema.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Resumo
    modifiable = sum(1 for v in schema.values() if not v['read_only'])
    
    print(f"\n✓ Análise completa:")
    print(f"  - Total campos: {len(schema)}")
    print(f"  - Modificáveis: {modifiable}")
    print(f"  - Read-only: {len(schema) - modifiable}")
    print(f"  - Mensagens processadas: {len(messages)}")
    print(f"\n✓ Salvo em: results/k1max_protocol_schema.json")
    
    # Top 10 campos mais atualizados
    print("\n📈 Top 10 campos mais atualizados:")
    sorted_fields = sorted(schema.items(), 
                          key=lambda x: x[1]['update_frequency'], 
                          reverse=True)[:10]
    
    for i, (key, info) in enumerate(sorted_fields, 1):
        ro = "🔒" if info['read_only'] else "✏️ "
        print(f"  {i:2d}. {ro} {key:30s} ({info['update_frequency']} vezes)")

if __name__ == "__main__":
    print("=== EXTRAÇÃO SCHEMA PROTOCOLO ===\n")
    extract_schema()