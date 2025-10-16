# test_metaverso_live.py
import yaml
from src.adapters.metaverso_api_client import MetaversoClient

# Carregar config
with open('config/config.yaml') as f:
    cfg = yaml.safe_load(f)

client = MetaversoClient('config/config.yaml')

# Teste autenticação
if client.login():
    print("✓ Autenticado na API Metaverso")
    
    # Teste validação token
    if client.validate_token():
        print("✓ Token válido")
    
    # Teste listagem usuários
    users = client.list_users()
    print(f"✓ {len(users)} usuários encontrados")
    
    # Teste fila impressão
    queue = client.get_print_queue()
    print(f"✓ {len(queue)} objetos na fila")
else:
    print("✗ Falha autenticação")