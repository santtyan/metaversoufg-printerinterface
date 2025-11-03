"""Teste download do primeiro objeto da fila"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.metaverso_client import MetaversoAPIClient

def test_download_first():
    """Baixa primeiro objeto da fila"""
    try:
        print("=== DOWNLOAD PRIMEIRO OBJETO ===\n")
        
        client = MetaversoAPIClient()
        client.authenticate()
        
        # 1. Buscar objetos COM arquivos
        print("1. Buscando objetos com arquivos...")
        objects = client.get_printable_objects(include_file=True)
        
        if not objects:
            print("❌ Fila vazia")
            return
        
        # 2. Pegar primeiro objeto
        first_obj = objects[0]
        object_id = first_obj.get('object_id')
        file_data = first_obj.get('file')  # Base64
        
        print(f"2. Objeto selecionado: {object_id}")
        print(f"   Tamanho base64: {len(file_data) if file_data else 0} chars")
        
        # 3. Salvar arquivo GLB
        print("3. Salvando arquivo GLB...")
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        glb_path = client.save_object_file(file_data, object_id, str(models_dir))
        
        if Path(glb_path).exists():
            size_mb = Path(glb_path).stat().st_size / 1024 / 1024
            print(f"✅ Arquivo salvo: {glb_path}")
            print(f"   Tamanho: {size_mb:.2f} MB")
            
            # 4. Marcar como imprimindo
            print("4. Marcando como imprimindo...")
            client.mark_object_printing(object_id)
            print("✅ Status atualizado")
            
            return glb_path
        else:
            print("❌ Falha ao salvar arquivo")
            return None
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    glb_path = test_download_first()
    if glb_path:
        print(f"\n🎯 SUCESSO: {glb_path}")
        print("Pronto para converter GLB→STL e fatiar!")
    else:
        print("\n❌ Falhou no download")
