# src/k1max/test_k1max.py
"""
Testes - K1 Max Controller 

EXECUTAR:
    cd C:\Projetos\metaversoufg-printerinterface
    .\venv_k1max_automation\Scripts\Activate
    pip install websockets (primeira vez)
    cd src
    python k1max/test_k1max.py
"""

import sys
from pathlib import Path

# Adicionar src/ ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from k1max.k1max_controller import K1MaxController

def test_reading_functions():
    """Testa funções de leitura (WebSocket)"""
    print("\n" + "="*60)
    print("FUNÇÕES DE LEITURA (WebSocket)")
    print("="*60)
    
    controller = K1MaxController()
    
    try:
        print("\n[1/2] is_printing()...")
        printing = controller.is_printing()
        print(f"✓ Resultado: {'IMPRIMINDO' if printing else 'PARADA'}")
        
        print("\n[2/2] is_ready()...")
        ready = controller.is_ready()
        print(f"✓ Resultado: {'PRONTA' if ready else 'NÃO PRONTA'}")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def test_writing_functions():
    """Testa funções de escrita"""
    print("\n" + "="*60)
    print("FUNÇÕES DE ESCRITA")
    print("="*60)
    
    controller = K1MaxController()
    
    print("\n[3/5] set_material('PLA')...")
    try:
        result = controller.set_material("PLA")
        print(f"✓ Resultado: {result}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[4/5] set_temperature(210, 60)...")
    try:
        result = controller.set_temperature(210, 60)
        print(f"✓ Resultado: {result}")
    except Exception as e:
        print(f"✗ Erro: {e}")
    
    print("\n[5/5] send_print_job()...")
    print("⚠️  Requer arquivo GLB/STL válido em models/")
    print("⚠️  Executar manualmente: controller.send_print_job('models/teste.glb')")

def main():
    print("\n" + "="*60)
    print("K1 MAX CONTROLLER - TESTE DAS 5 FUNÇÕES")
    print("="*60)
    
    test_reading_functions()
    test_writing_functions()
    
    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60)
    print("\nPara testar send_print_job() com arquivo real:")
    print(">>> from k1max.k1max_controller import K1MaxController")
    print(">>> controller = K1MaxController()")
    print(">>> controller.send_print_job('../models/charmander(1).glb')")

if __name__ == "__main__":
    main()