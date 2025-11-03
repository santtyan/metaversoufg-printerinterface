"""Download GLB corrigido - endpoint /v1/objects"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def download_glb_final():
    """Download GLB usando endpoint correto"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        # Endpoint correto
        response = client.session.get(
            f"{client.base_url}/objects",
            params={"with_file": "true"},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        objects = data['data']  # Array está em 'data'
        
        print("=== DOWNLOAD GLB FINAL ===\n")
        print(f"Objetos disponíveis: {len(objects)}")
        
        if objects:
            obj = objects[0]
            object_id = obj.get('object_id')
            object_file_url = obj.get('object_file')
            
            print(f"Object ID: {object_id}")
            print(f"URL: {object_file_url[:80]}...")
            
            # Substituir hostname interno por externo
            external_url = object_file_url.replace(
                'metaversoufg-minio:9000',
                'metaverso.medialab.ufg.br:9000'
            )
            
            print("Tentando download...")
            
            # Tentar download
            dl_response = requests.get(external_url, timeout=30)
            
            if dl_response.status_code == 200:
                # Salvar arquivo
                models_dir = Path("models")
                models_dir.mkdir(exist_ok=True)
                glb_path = models_dir / f"{object_id}.glb"
                
                with open(glb_path, 'wb') as f:
                    f.write(dl_response.content)
                
                size_mb = glb_path.stat().st_size / 1024 / 1024
                print(f"✅ DOWNLOAD SUCESSO!")
                print(f"   Arquivo: {glb_path}")
                print(f"   Tamanho: {size_mb:.2f} MB")
                
                # Marcar como imprimindo (opcional)
                # client.mark_object_printing(object_id)
                
                return str(glb_path)
            else:
                print(f"❌ Download falhou: {dl_response.status_code}")
                
                # Se falhou, tentar sem substituição (URL original)
                print("Tentando URL original...")
                dl_response2 = requests.get(object_file_url, timeout=30)
                
                if dl_response2.status_code == 200:
                    models_dir = Path("models")
                    models_dir.mkdir(exist_ok=True)
                    glb_path = models_dir / f"{object_id}.glb"
                    
                    with open(glb_path, 'wb') as f:
                        f.write(dl_response2.content)
                    
                    size_mb = glb_path.stat().st_size / 1024 / 1024
                    print(f"✅ URL ORIGINAL FUNCIONOU!")
                    print(f"   Arquivo: {glb_path}")
                    print(f"   Tamanho: {size_mb:.2f} MB")
                    
                    return str(glb_path)
                else:
                    print(f"❌ URL original também falhou: {dl_response2.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    glb_path = download_glb_final()
    if glb_path:
        print(f"\n🎯 GLB BAIXADO COM SUCESSO!")
        print(f"Arquivo: {glb_path}")
        print("\n🚀 PRONTO PARA PIPELINE COMPLETO:")
        print("   GLB → STL → G-code → Impressão")
