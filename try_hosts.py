"""Tentar diferentes hostnames para MinIO"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def try_different_hosts():
    """Tenta diferentes hostnames para acessar MinIO"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        objects = client.get_printable_objects(include_file=True)
        object_id = objects[0]['object_id']
        original_url = objects[0]['object_file']
        
        print("=== TESTE DIFERENTES HOSTNAMES ===\n")
        print(f"URL original: {original_url[:80]}...")
        
        # Diferentes hostnames para tentar
        hosts_to_try = [
            'metaverso.medialab.ufg.br',      # Já testamos - 403
            'metaverso.medialab.ufg.br:9000', # Com porta explícita
            'minio.metaverso.medialab.ufg.br', # Subdomínio
            'files.metaverso.medialab.ufg.br', # Files subdomain
        ]
        
        for host in hosts_to_try:
            try:
                # Substituir hostname
                test_url = original_url.replace('metaversoufg-minio:9000', host)
                
                print(f"\nTestando: {host}")
                print(f"URL: {test_url[:80]}...")
                
                response = requests.get(test_url, timeout=15)
                
                if response.status_code == 200:
                    print(f"✅ SUCESSO: {host}")
                    
                    # Salvar arquivo
                    glb_path = Path("models") / f"{object_id}.glb"
                    with open(glb_path, 'wb') as f:
                        f.write(response.content)
                    
                    size_mb = glb_path.stat().st_size / 1024 / 1024
                    print(f"   Arquivo salvo: {size_mb:.2f} MB")
                    
                    # Marcar como imprimindo
                    client.mark_object_printing(object_id)
                    
                    return str(glb_path)
                else:
                    print(f"   {response.status_code}: {response.reason}")
                    
            except Exception as e:
                print(f"   Erro: {e}")
        
        print("\n❌ Nenhum hostname funcionou")
        return None
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

if __name__ == "__main__":
    glb_path = try_different_hosts()
    if glb_path:
        print(f"\n🎯 ARQUIVO BAIXADO!")
        print(f"Caminho: {glb_path}")
        print("Pronto para pipeline completo!")
    else:
        print("\n💡 Pode precisar falar com Guilherme sobre acesso ao MinIO")
