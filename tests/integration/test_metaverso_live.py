# test_metaverso_live.py
import yaml
from src.adapters.metaverso_client import MetaversoAPIClient

# Carregar config
with open('config/config.yaml') as f:
    cfg = yaml.safe_load(f)

client = MetaversoAPIClient('config/config.yaml')

print("\n=== TESTE METAVERSO API CLIENT ===\n")

# Teste autenticação
try:
    print("1. Testando autenticação...")
    if client.authenticate():
        print("   ✓ Autenticado na API Metaverso")
        print(f"   Token: {client.token[:20]}..." if client.token else "   Token: None")
    
        # Teste validação token
        print("\n2. Testando validação token...")
        if client.validate_token():
            print("   ✓ Token válido")
        
        # Teste health check
        print("\n3. Testando health check...")
        health = client.health_check()
        print(f"   ✓ Health: {health}")
        
        # Teste objetos imprimíveis
        print("\n4. Testando buscar objetos imprimíveis...")
        objects = client.get_printable_objects()
        print(f"   ✓ {len(objects)} objetos na fila")
        
        if objects:
            print("\n   Primeiro objeto:")
            first = objects[0]
            for key, value in first.items():
                if key != 'file':
                    print(f"     {key}: {value}")
    else:
        print("   ✗ Falha autenticação")
        
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ TESTE CONCLUÍDO")
