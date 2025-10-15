# test_menu.py

"""
Menu de Testes - API Metaverso UFG

EXECUTAR:
1. cd C:\Projetos\metaversoufg-printerinterface
2. .\venv_k1max_automation\Scripts\Activate
3. pip install pyyaml (primeira vez)
4. python src\test_menu.py

CONFIGURAR:
Editar config/config.yaml com credenciais corretas
"""

from adapters.metaverso_api_client import MetaversoAPIClient

client = MetaversoAPIClient()
client.authenticate()

while True:
    print("\n" + "="*50)
    print("1. GET /printer/printable")
    print("2. PATCH /printer/printing/{id}")
    print("3. PATCH /printer/print/{id}")
    print("4. Workflow completo")
    print("0. Sair")
    print("="*50)
    
    choice = input("→ ")
    
    if choice == "0":
        break
    
    elif choice == "1":
        print("\n[GET /printer/printable]")
        try:
            objs = client.get_printable_objects()
            print(f"✓ {len(objs)} objetos na fila")
            for o in objs[:5]:
                print(f"  - {o.get('name')} (ID: {o['object_id'][:8]}...)")
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    elif choice == "2":
        print("\n[PATCH /printer/printing/{id}]")
        try:
            objs = client.get_printable_objects()
            if not objs:
                print("✗ Fila vazia")
                continue
            
            print("Objetos disponíveis:")
            for i, o in enumerate(objs):
                print(f"  {i+1}. {o.get('name')} (ID: {o['object_id'][:8]}...)")
            
            idx = input("Número do objeto: ").strip()
            if idx.isdigit() and 0 < int(idx) <= len(objs):
                obj_id = objs[int(idx)-1]['object_id']
                try:
                    client.mark_object_printing(obj_id)
                    print("✓ Marcado PRINTING")
                except Exception as e:
                    print(f"✗ Erro: {e}")
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    elif choice == "3":
        print("\n[PATCH /printer/print/{id}]")
        obj_id = input("Object ID: ").strip()
        try:
            client.mark_object_printable(obj_id)
            print("✓ Marcado PRINTABLE")
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    elif choice == "4":
        print("\n[WORKFLOW COMPLETO]")
        try:
            objs = client.get_printable_objects()
            if not objs:
                print("✗ Fila vazia")
                continue
            
            obj = objs[0]
            obj_id = obj['object_id']
            print(f"1. Objeto: {obj.get('name')}")
            
            client.mark_object_printing(obj_id)
            print("2. ✓ Marcado PRINTING")
            
            input("   [ENTER para devolver à fila]")
            
            client.mark_object_printable(obj_id)
            print("3. ✓ Devolvido à fila")
        except Exception as e:
            print(f"✗ Erro: {e}")