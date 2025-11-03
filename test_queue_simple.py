"""Teste simples da fila de impressão Metaverso UFG"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def test_queue():
    """Testa consulta à fila de impressão"""
    try:
        print("=== TESTE FILA METAVERSO UFG ===\n")
        
        # 1. Inicializar cliente
        print("1. Inicializando cliente...")
        client = MetaversoAPIClient()
        
        # 2. Autenticar
        print("2. Autenticando...")
        client.authenticate()
        print("✅ Autenticação OK")
        
        # 3. Consultar fila SEM arquivos (mais rápido)
        print("3. Consultando fila (sem arquivos)...")
        objects = client.get_printable_objects(include_file=False)
        
        print(f"✅ Fila consultada: {len(objects)} objetos")
        
        # 4. Mostrar resumo
        if objects:
            print("\nObjetos na fila:")
            for i, obj in enumerate(objects):
                print(f"  {i+1}. ID: {obj.get('object_id', 'N/A')}")
                print(f"     Nome: {obj.get('name', 'N/A')}")
                print(f"     Status: {obj.get('status', 'N/A')}")
                print()
        else:
            print("⚠️ Fila vazia")
            
        return len(objects)
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    count = test_queue()
    print(f"\nResultado: {count} objetos encontrados")
