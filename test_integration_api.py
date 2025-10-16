# test_integration_api.py
"""
Teste integração API Metaverso (SEM impressora)
"""
import sys
sys.path.insert(0, 'src')

from adapters.metaverso_client import MetaversoAPIClient

def test_api_connection():
    """Testa conexão e autenticação"""
    print("=== TESTE API METAVERSO ===\n")
    
    api = MetaversoAPIClient()
    
    try:
        # 1. Autenticação
        print("1. Tentando autenticação...")
        api.authenticate()
        print("✅ Autenticação bem-sucedida\n")
        
        # 2. Validar token
        print("2. Validando token...")
        if api.validate_token():
            print("✅ Token válido\n")
        else:
            print("✗ Token inválido\n")
        
        # 3. Health check
        print("3. Health check...")
        if api.health_check():
            print("✅ API operacional\n")
        else:
            print("⚠️ API com problemas\n")
        
        # 4. Objetos disponíveis
        print("4. Consultando objetos disponíveis...")
        objetos = api.get_printable_objects()
        
        if objetos:
            print(f"✅ {len(objetos)} objetos na fila\n")
            
            # Mostrar primeiros 3
            for i, obj in enumerate(objetos[:3], 1):
                obj_id = obj.get('object_id', obj.get('id', 'N/A'))
                name = obj.get('name', obj.get('object_name', 'sem nome'))
                print(f"   {i}. {name} (ID: {obj_id})")
            
            if len(objetos) > 3:
                print(f"   ... e mais {len(objetos) - 3} objetos")
        else:
            print("⚠️ Nenhum objeto disponível")
        
        # 5. Métodos disponíveis
        print("\n5. Métodos disponíveis:")
        methods = ['authenticate', 'validate_token', 'health_check', 
                  'get_printable_objects', 'get_object_details',
                  'mark_object_printing', 'mark_object_printable',
                  'save_object_file']
        for method in methods:
            print(f"   ✓ {method}()")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        print(f"   Tipo: {type(e).__name__}")
        print("\nVerificar credenciais em config/config.yaml")

if __name__ == "__main__":
    test_api_connection()