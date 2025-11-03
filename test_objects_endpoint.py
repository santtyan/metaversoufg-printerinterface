"""Testar endpoint correto do Swagger"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def test_objects_endpoint():
    """Testa endpoint /v1/objects com file data"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        print("=== TESTE ENDPOINT /v1/objects ===\n")
        
        # Testar diferentes parâmetros para incluir arquivo
        params_to_try = [
            {"with_file": "true"},
            {"include_file": "true"}, 
            {"file": "true"},
            {"file_data": "true"}
        ]
        
        for params in params_to_try:
            try:
                print(f"Testando parâmetros: {params}")
                
                response = client.session.get(
                    f"{client.base_url}/objects",
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    objects = data.get('data', data)  # Pode estar em 'data' wrapper
                    
                    print(f"✅ SUCESSO: {len(objects)} objetos")
                    
                    if objects and isinstance(objects, list):
                        obj = objects[0]
                        print(f"   Campos: {list(obj.keys())}")
                        
                        # Procurar campo com arquivo
                        for key, value in obj.items():
                            if isinstance(value, str) and len(str(value)) > 500:
                                print(f"   Campo longo '{key}': {len(str(value))} chars")
                                
                                # Se parece base64, tentar decodificar
                                if key in ['file', 'file_data', 'glb_data', 'model_data']:
                                    try:
                                        import base64
                                        file_data = base64.b64decode(value)
                                        
                                        # Salvar teste
                                        object_id = obj.get('id') or obj.get('object_id') or 'test'
                                        glb_path = Path("models") / f"{object_id}.glb"
                                        
                                        with open(glb_path, 'wb') as f:
                                            f.write(file_data)
                                        
                                        size_mb = glb_path.stat().st_size / 1024 / 1024
                                        print(f"   ✅ GLB DECODIFICADO: {size_mb:.2f} MB")
                                        return str(glb_path)
                                        
                                    except Exception as e:
                                        print(f"   Base64 decode falhou: {e}")
                    
                    return "sucesso_sem_arquivo"
                else:
                    print(f"   {response.status_code}: {response.reason}")
                    
            except Exception as e:
                print(f"   Erro: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

if __name__ == "__main__":
    result = test_objects_endpoint()
    if result and result.endswith('.glb'):
        print(f"\n🎯 GLB BAIXADO VIA /v1/objects!")
        print(f"Arquivo: {result}")
