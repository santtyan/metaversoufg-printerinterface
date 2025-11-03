"""Debug da consulta API"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def debug_api():
    """Debug das consultas API"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        print("=== DEBUG CONSULTAS API ===\n")
        
        # 1. Testar sem arquivos
        print("1. Sem arquivos (include_file=False):")
        objects_no_file = client.get_printable_objects(include_file=False)
        print(f"   Objetos: {len(objects_no_file)}")
        if objects_no_file:
            print(f"   Campos: {list(objects_no_file[0].keys())}")
        
        # 2. Testar com arquivos
        print("\n2. Com arquivos (include_file=True):")
        objects_with_file = client.get_printable_objects(include_file=True)
        print(f"   Objetos: {len(objects_with_file)}")
        if objects_with_file:
            obj = objects_with_file[0]
            print(f"   Campos: {list(obj.keys())}")
            print(f"   Campo 'file': {type(obj.get('file'))}")
            print(f"   Campo 'file' existe: {'file' in obj}")
            
            # Ver todos os campos que podem conter arquivo
            for key, value in obj.items():
                if isinstance(value, str) and len(str(value)) > 100:
                    print(f"   Campo longo '{key}': {len(str(value))} chars")
                    
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api()
