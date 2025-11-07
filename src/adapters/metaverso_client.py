# metaverso_api_client.py
import requests
import base64
import os
import yaml
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class MetaversoAPIClient:
    def __init__(self, config_path="config/config.yaml"):
        # Carregar config
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        
        self.base_url = cfg['api']['base_url']
        self.timeout = cfg['api']['timeout']
        self.credentials = cfg['credentials']
        self.models_dir = Path(cfg['paths']['project_root']) / cfg['paths']['models']
        
        self.session = requests.Session()
        
        # Retry automÃ¡tico
        retry = Retry(
            total=3, 
            backoff_factor=0.5, 
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        
        self.token = None
    
    def authenticate(self):
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
        if not self.token:
            self.authenticate()
        
        r = self.session.get(
            f"{self.base_url}/printer/printable",
            params={"with_file": str(include_file).lower()},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()
    
    def mark_object_printing(self, object_id):
        r = self.session.patch(
            f"{self.base_url}/printer/printing/{object_id}", 
            timeout=self.timeout
        )
        r.raise_for_status()
        return True
    
    def mark_object_printable(self, object_id):
        r = self.session.patch(
            f"{self.base_url}/printer/print/{object_id}", 
            timeout=self.timeout
        )
        r.raise_for_status()
        return True
    
    def get_object_details(self, object_id):
        """GET /v1/objects/{id} - Retorna metadados completos"""
        if not self.token:
            self.authenticate()
        
        r = self.session.get(
            f"{self.base_url}/objects/{object_id}", 
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()
    
    def save_object_file(self, base64_content, object_id, output_dir=None):
        """Decodifica base64 e salva arquivo GLB localmente"""
        if output_dir is None:
            output_dir = self.models_dir
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{object_id}.glb")
        
        file_data = base64.b64decode(base64_content)
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        return file_path if os.path.exists(file_path) else None
    
    def validate_token(self):
        """GET /v1/auth/validate - Verifica se token Ã© vÃ¡lido"""
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
        """Verifica se API estÃ¡ acessÃ­vel"""
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
    
    print("[1/5] Autenticando...")
    client.authenticate()
    print("âœ“ Autenticado")
    
    print("\n[2/5] Validando token...")
    print(f"âœ“ Token {'vÃ¡lido' if client.validate_token() else 'invÃ¡lido'}")
    
    print("\n[3/5] Health check API...")
    print(f"âœ“ API {'acessÃ­vel' if client.health_check() else 'offline'}")
    
    print("\n[4/5] Consultando fila...")
    objs = client.get_printable_objects()
    print(f"âœ“ {len(objs)} objetos na fila")
    
    if objs:
        obj = objs[0]
        obj_id = obj['object_id']
        
        print(f"\n[5/5] Testando workflow com {obj_id[:8]}...")
        client.mark_object_printing(obj_id)
        print("  âœ“ Marcado PRINTING")
        client.mark_object_printable(obj_id)
        print("  âœ“ Devolvido Ã  fila")
    
    print("\n" + "="*60)
    print("Teste concluÃ­do.")
