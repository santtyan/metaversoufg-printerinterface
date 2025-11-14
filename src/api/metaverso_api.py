"""
Wrapper MetaversoAPI - Interface simplificada (independente)
"""
import logging
import requests
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

def createMetaversoAPI(cfg):
    """Factory function - cria wrapper da API"""
    return MetaversoAPIWrapper(cfg)

class MetaversoAPIWrapper:
    """Wrapper standalone para Metaverso API"""
    
    def __init__(self, cfg):
        self.cfg = cfg
        self.base_url = cfg['metaverso']['backend_url']
        self.username = cfg['metaverso']['username']
        self.password = cfg['metaverso']['password']
        self.token = None
        
        # Autenticar
        self._authenticate()
        logger.info("✓ MetaversoAPI inicializado")
    
    def _authenticate(self):
        """Autentica na API"""
        url = f"{self.base_url}/auth/login"
        payload = {
            "email": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            self.token = data.get('accessToken')
            logger.info("✓ Autenticado com sucesso")
        except Exception as e:
            logger.error(f"✗ Falha na autenticação: {e}")
            raise
    
    def getObjectFromServer(self) -> Optional[Dict]:
        """Busca próximo objeto da fila"""
        url = f"{self.base_url}/printer/printable"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"with_file": "true"}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            objects = response.json()
            
            if not objects or len(objects) == 0:
                return None
            
            # Retornar primeiro objeto
            obj = objects[0]
            return {
                'object_id': obj.get('object_id'),
                'object_name': obj.get('object_name'),
                'glb_url': obj.get('object_file'),
                'glb_data': obj.get('file_data')
            }
        except Exception as e:
            logger.error(f"✗ Erro ao buscar fila: {e}")
            return None
    
    def informPrinting(self, object_id: str) -> bool:
        """Notifica backend que objeto foi enviado"""
        url = f"{self.base_url}/printer/{object_id}/printing"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info(f"✓ Objeto {object_id} marcado como imprimindo")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao notificar: {e}")
            return False
