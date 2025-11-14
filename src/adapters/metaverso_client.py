# metaverso_client.py
import requests
import base64
import os
import yaml
import json
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class MetaversoAPIClient:
    def __init__(self, config_path="config/config.yaml"):
        # Carregar configuração
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        
        self.base_url = cfg['api']['base_url']
        self.timeout = cfg['api']['timeout']
        self.credentials = cfg['credentials']
        self.models_dir = Path(cfg['paths']['project_root']) / cfg['paths']['models']
        
        self.session = requests.Session()
        
        # Configurar retry automático para falhas temporárias
        retry = Retry(
            total=3, 
            backoff_factor=0.5, 
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        
        self.token = None
    
    def authenticate(self):
        """Autentica na API e armazena token JWT"""
        r = self.session.post(
            f"{self.base_url}/auth/login",
            json=self.credentials,
            timeout=self.timeout
        )
        r.raise_for_status()
        self.token = r.json()["accessToken"]
        self.session.headers["Authorization"] = f"Bearer {self.token}"
        return True
    
    def get_printable_objects(self, include_file=False):
        """Busca objetos na fila de impressão"""
        if not self.token:
            self.authenticate()
        
        params = {"with_file": str(include_file).lower()}
        
        # SOLUÇÃO MinIO: usar buffer ao invés de URL
        if include_file:
            params["file_method"] = "buffer"
            params["file_encoding"] = "base64"
        
        r = self.session.get(
            f"{self.base_url}/printer/printable",
            params=params,
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()
    
    def mark_object_printing(self, object_id):
        """Marca objeto como 'em impressão'"""
        r = self.session.patch(
            f"{self.base_url}/printer/printing/{object_id}", 
            timeout=self.timeout
        )
        r.raise_for_status()
        return True
    
    def mark_object_printable(self, object_id):
        """Devolve objeto para fila (marca como 'imprimível')"""
        r = self.session.patch(
            f"{self.base_url}/printer/print/{object_id}", 
            timeout=self.timeout
        )
        r.raise_for_status()
        return True
    
    def get_object_details(self, object_id):
        """GET /v1/objects/{id} - Retorna metadados completos do objeto"""
        if not self.token:
            self.authenticate()
        
        r = self.session.get(
            f"{self.base_url}/objects/{object_id}", 
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()
    
    def save_object_file(self, base64_content, object_id, output_dir=None):
        """Decodifica base64 e salva arquivo GLB no disco com validação"""
        if output_dir is None:
            output_dir = self.models_dir
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = Path(output_dir) / f"{object_id}.glb"
        
        try:
            # Remover prefixo data URL se existir
            if base64_content.startswith('data:'):
                base64_content = base64_content.split(',')[1]
            
            # Decodificar e salvar
            file_data = base64.b64decode(base64_content)
            with open(file_path, "wb") as f:
                f.write(file_data)
            
            # Validar GLB header
            import trimesh
            trimesh.load(str(file_path))
            
            return str(file_path)
            
        except Exception as e:
            # GLB corrompido - deletar e retornar None
            if file_path.exists():
                file_path.unlink()
            return None
    
    def validate_token(self):
        """GET /v1/auth/validate - Verifica se token JWT é válido"""
        if not self.token:
            return False
        
        try:
            r = self.session.get(
                f"{self.base_url}/auth/validate", 
                timeout=10
            )
            return r.status_code == 200
        except:
            return False
    
    def health_check(self):
        """Verifica se API está acessível"""
        try:
            r = self.session.get(
                self.base_url.replace("/v1", ""), 
                timeout=5
            )
            return r.status_code == 200
        except:
            return False


if __name__ == "__main__":
    client = MetaversoAPIClient()
    
    print("🎯 TESTE: Download GLB via file_method=buffer")
    print("="*60)
    
    print("[1/7] Autenticando...")
    client.authenticate()
    print("✓ Autenticado")
    
    print("\n[2/7] Validando token...")
    print(f"✓ Token {'válido' if client.validate_token() else 'inválido'}")
    
    print("\n[3/7] Health check API...")
    print(f"✓ API {'acessível' if client.health_check() else 'offline'}")
    
    print("\n[4/7] Consultando fila SEM arquivo...")
    objs = client.get_printable_objects(include_file=False)
    print(f"✓ {len(objs)} objetos na fila")
    
    print("\n[5/7] Consultando fila COM arquivo (buffer)...")
    try:
        objs_with_file = client.get_printable_objects(include_file=True)
        print(f"✓ {len(objs_with_file)} objetos retornados com arquivo")
        
        if objs_with_file:
            obj = objs_with_file[0]
            object_id = obj['object_id']
            object_file = obj.get('object_file', '')
            
            print(f"\n[6/7] Analisando primeiro objeto: {object_id[:8]}...")
            print(f"Campo object_file: {len(object_file)} chars")
            print(f"Primeiros 100 chars: {object_file[:100]}")
            
            if object_file:
                print("\n[7/7] Salvando GLB...")
                glb_path = client.save_object_file(object_file, object_id)
                
                if glb_path:
                    size_mb = Path(glb_path).stat().st_size / 1024 / 1024
                    print(f"✅ SUCESSO! GLB salvo: {glb_path}")
                    print(f"   Tamanho: {size_mb:.2f} MB")
                    
                    # Marcar como printing para teste
                    client.mark_object_printing(object_id)
                    print(f"✓ Objeto marcado como PRINTING")
                    
                    # Devolver para fila
                    client.mark_object_printable(object_id)
                    print(f"✓ Objeto devolvido à fila")
                    
                    print(f"\n🎯 PIPELINE DESBLOQUEADO!")
                    print(f"GLB → STL → G-code → Impressão PRONTO!")
                else:
                    print("❌ Falha ao salvar/validar GLB")
            else:
                print("⚠ object_file vazio")
        else:
            print("⚠ Nenhum objeto na fila")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Teste concluído.")