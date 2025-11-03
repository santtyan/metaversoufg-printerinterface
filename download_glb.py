"""Download GLB via URL modificada"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def download_glb():
    """Baixa GLB via URL do object_file"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        objects = client.get_printable_objects(include_file=True)
        
        if objects:
            obj = objects[0]
            object_id = obj.get('object_id')
            minio_url = obj.get('object_file')
            
            print("=== DOWNLOAD GLB VIA URL ===\n")
            print(f"Object ID: {object_id}")
            print(f"URL MinIO: {minio_url[:100]}...")
            
            # Tentar substituir hostname interno por externo
            external_url = minio_url.replace(
                'metaversoufg-minio:9000', 
                'metaverso.medialab.ufg.br:9000'
            )
            
            print(f"URL Externa: {external_url[:100]}...")
            
            # Download
            print("Baixando arquivo...")
            response = requests.get(external_url, timeout=30)
            response.raise_for_status()
            
            # Salvar
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)
            glb_path = models_dir / f"{object_id}.glb"
            
            with open(glb_path, 'wb') as f:
                f.write(response.content)
            
            size_mb = glb_path.stat().st_size / 1024 / 1024
            print(f"✅ Arquivo salvo: {glb_path}")
            print(f"   Tamanho: {size_mb:.2f} MB")
            
            # Marcar como imprimindo
            client.mark_object_printing(object_id)
            print("✅ Status atualizado para 'imprimindo'")
            
            return str(glb_path)
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    glb_path = download_glb()
    if glb_path:
        print(f"\n🎯 SUCESSO: GLB baixado!")
        print(f"Arquivo: {glb_path}")
        print("Pronto para pipeline completo!")
