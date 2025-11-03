"""Investigar object_file"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def investigate_file():
    """Investiga conteúdo do object_file"""
    try:
        client = MetaversoAPIClient()
        client.authenticate()
        
        objects = client.get_printable_objects(include_file=True)
        
        if objects:
            obj = objects[0]
            object_file = obj.get('object_file')
            
            print("=== INVESTIGAÇÃO object_file ===\n")
            print(f"Tipo: {type(object_file)}")
            print(f"Tamanho: {len(str(object_file))} chars")
            print(f"Primeiros 100 chars:")
            print(f"'{str(object_file)[:100]}'")
            print(f"\nÚltimos 50 chars:")
            print(f"'{str(object_file)[-50:]}'")
            
            # Tentar como URL ou path
            if isinstance(object_file, str):
                if object_file.startswith('http'):
                    print(f"\n🔗 Parece ser URL: {object_file}")
                elif object_file.startswith('/') or object_file.startswith('\\'):
                    print(f"\n📁 Parece ser caminho: {object_file}")
                else:
                    print(f"\n❓ Formato desconhecido")
                    
    except Exception as e:
        print(f"❌ ERRO: {e}")

if __name__ == "__main__":
    investigate_file()
