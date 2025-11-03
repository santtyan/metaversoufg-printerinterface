"""Debug estrutura de resposta"""

import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def debug_response_structure():
    """Debug da estrutura da resposta"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        response = client.session.get(
            f"{client.base_url}/objects",
            params={"with_file": "true"},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        print("=== DEBUG ESTRUTURA RESPOSTA ===\n")
        print(f"Tipo da resposta: {type(data)}")
        print(f"Chaves principais: {list(data.keys()) if isinstance(data, dict) else 'não é dict'}")
        
        # Se for dict, procurar array de objetos
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"\nChave '{key}':")
                print(f"  Tipo: {type(value)}")
                if isinstance(value, list):
                    print(f"  Tamanho lista: {len(value)}")
                    if value:
                        print(f"  Primeiro item: {type(value[0])}")
                        if isinstance(value[0], dict):
                            print(f"  Campos: {list(value[0].keys())}")
                            
                            # Verificar se tem object_file
                            obj = value[0]
                            object_file = obj.get('object_file')
                            if object_file:
                                print(f"  object_file: {len(str(object_file))} chars")
                                print(f"  Primeiros 50: {str(object_file)[:50]}")
                elif isinstance(value, (str, int, float)):
                    print(f"  Valor: {value}")
        
        return data
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    data = debug_response_structure()
