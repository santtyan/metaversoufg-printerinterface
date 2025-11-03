"""Investigar object_file do endpoint /v1/objects"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def investigate_objects_file():
    """Investiga object_file do endpoint /v1/objects"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        # Usar endpoint correto
        response = client.session.get(
            f"{client.base_url}/objects",
            params={"with_file": "true"},
            timeout=30
        )
        response.raise_for_status()
        
        objects = response.json()
        
        print("=== INVESTIGAÇÃO /v1/objects ===\n")
        print(f"Total objetos: {len(objects)}")
        
        if objects:
            obj = objects[0]
            object_id = obj.get('object_id')
            object_file = obj.get('object_file')
            
            print(f"Object ID: {object_id}")
            print(f"object_file tipo: {type(object_file)}")
            print(f"object_file tamanho: {len(str(object_file))} chars")
            
            if isinstance(object_file, str):
                print(f"Primeiros 100 chars: {object_file[:100]}")
                print(f"Últimos 50 chars: {object_file[-50:]}")
                
                # Verificar se é URL ou base64
                if object_file.startswith('http'):
                    print("📡 É URL - tentando download...")
                    
                    # Tentar download direto
                    dl_response = requests.get(object_file, timeout=30)
                    
                    if dl_response.status_code == 200:
                        # Salvar arquivo
                        models_dir = Path("models")
                        models_dir.mkdir(exist_ok=True)
                        glb_path = models_dir / f"{object_id}.glb"
                        
                        with open(glb_path, 'wb') as f:
                            f.write(dl_response.content)
                        
                        size_mb = glb_path.stat().st_size / 1024 / 1024
                        print(f"✅ DOWNLOAD SUCESSO: {size_mb:.2f} MB")
                        print(f"   Arquivo: {glb_path}")
                        
                        return str(glb_path)
                    else:
                        print(f"❌ Download falhou: {dl_response.status_code}")
                
                elif len(object_file) > 1000:  # Pode ser base64
                    print("📦 Pode ser base64 - tentando decodificar...")
                    
                    try:
                        import base64
                        file_data = base64.b64decode(object_file)
                        
                        # Salvar arquivo
                        models_dir = Path("models")
                        models_dir.mkdir(exist_ok=True)
                        glb_path = models_dir / f"{object_id}.glb"
                        
                        with open(glb_path, 'wb') as f:
                            f.write(file_data)
                        
                        size_mb = glb_path.stat().st_size / 1024 / 1024
                        print(f"✅ BASE64 DECODIFICADO: {size_mb:.2f} MB")
                        print(f"   Arquivo: {glb_path}")
                        
                        return str(glb_path)
                        
                    except Exception as e:
                        print(f"❌ Base64 decode falhou: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    glb_path = investigate_objects_file()
    if glb_path:
        print(f"\n🎯 GLB OBTIDO SUCESSOS!")
        print(f"Pronto para pipeline completo: GLB → STL → G-code → Impressão!")
