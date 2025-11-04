# -*- coding: utf-8 -*-
import requests
import yaml
from pathlib import Path

config = yaml.safe_load(open('config/config.yaml', encoding='utf-8'))

API_BASE = config['api']['base_url']
QUEUE_ENDPOINT = config['api']['queue_endpoint']
AUTH_ENDPOINT = config['api']['auth_endpoint']
EMAIL = config['credentials']['email']
PASSWORD = config['credentials']['password']

print("=" * 70)
print("TESTE: Download via API Proxy")
print("=" * 70)

# Autenticar
auth_response = requests.post(
    f"{API_BASE}{AUTH_ENDPOINT}",
    json={"email": EMAIL, "password": PASSWORD},
    timeout=10
)

token = auth_response.json()['accessToken']
headers = {"Authorization": f"Bearer {token}"}

# Buscar fila
queue_response = requests.get(
    f"{API_BASE}{QUEUE_ENDPOINT}",
    headers=headers,
    timeout=10
)

objects = queue_response.json()
obj = objects[0]

print(f"\nObjeto: {obj['object_name']}")
print(f"ID: {obj['object_id']}")
print(f"MinIO URL (inacessivel): {obj['object_file']}")

# Estratégias de download via proxy
strategies = [
    ("Proxy direto", f"{API_BASE}/objects/{obj['object_id']}/file"),
    ("Proxy download", f"{API_BASE}/objects/{obj['object_id']}/download"),
    ("Printer download", f"{API_BASE}/printer/{obj['object_id']}/file"),
    ("Files endpoint", f"{API_BASE}/files/{obj['object_id']}"),
]

print("\n" + "=" * 70)
print("Testando estrategias de download via API proxy...")
print("=" * 70)

for name, url in strategies:
    print(f"\n[{name}]")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            size = len(response.content)
            
            print(f"Content-Type: {content_type}")
            print(f"Tamanho: {size:,} bytes")
            
            # Validar STL
            content_start = response.content[:100]
            is_stl = (
                content_start.startswith(b'\x00' * 5) or
                b'solid' in content_start.lower()
            )
            
            if is_stl:
                # Salvar
                output = Path("downloads") / f"{obj['object_id']}.stl"
                output.parent.mkdir(exist_ok=True)
                output.write_bytes(response.content)
                
                print(f"SUCESSO! Arquivo STL baixado")
                print(f"Salvo em: {output}")
                print("\n" + "=" * 70)
                print("PIPELINE DESBLOQUEADO!")
                print(f"Endpoint correto: {url}")
                print("=" * 70)
                exit(0)
            else:
                print(f"Nao e STL. Primeiros bytes: {content_start[:30]}")
        
        elif response.status_code == 404:
            print("Endpoint nao existe")
        else:
            print(f"Erro: {response.text[:100]}")
            
    except Exception as e:
        print(f"Excecao: {e}")

print("\n" + "=" * 70)
print("BLOCKER: Nenhum endpoint de proxy funcionou")
print("Acao necessaria: Contatar Guilherme para implementar proxy")
print("=" * 70)
