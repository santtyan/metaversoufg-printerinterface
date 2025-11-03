"""Testar endpoint de download via API"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def test_api_download():
    """Tenta baixar via API diretamente"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        objects = client.get_printable_objects(include_file=True)
        object_id = objects[0]['object_id']
        
        print("=== TESTE DOWNLOAD VIA API ===\n")
        
        # Testar endpoints possíveis
        endpoints = [
            f"/objects/{object_id}/download",
            f"/objects/{object_id}/file", 
            f"/printer/objects/{object_id}/download",
            f"/v1/objects/{object_id}/download"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{client.base_url}{endpoint}"
                print(f"Testando: {url}")
                
                response = client.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ FUNCIONA: {endpoint}")
                    print(f"   Content-Type: {response.headers.get('content-type')}")
                    print(f"   Tamanho: {len(response.content)} bytes")
                    
                    # Salvar arquivo
                    glb_path = Path("models") / f"{object_id}.glb"
                    with open(glb_path, 'wb') as f:
                        f.write(response.content)
                    
                    return str(glb_path)
                else:
                    print(f"   {response.status_code}: {response.reason}")
                    
            except Exception as e:
                print(f"   Erro: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

if __name__ == "__main__":
    glb_path = test_api_download()
    if glb_path:
        print(f"\n🎯 SUCESSO VIA API!")
        print(f"Arquivo: {glb_path}")
