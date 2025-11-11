#!/usr/bin/env python3
"""
TESTE CRÍTICO: Valida se G-code abre nativamente no Creality Print
Baseado na descoberta do Alércio
"""

import subprocess
import time
from pathlib import Path

def test_native_gcode_open():
    """Testa abertura nativa de G-code"""
    
    # Usar G-code existente
    gcode_path = Path("data/output/cube.gcode")
    
    if not gcode_path.exists():
        print(f"❌ G-code não encontrado: {gcode_path}")
        print("\nTentando outro arquivo...")
        gcode_path = Path("data/output/benchy_test.gcode")
        
        if not gcode_path.exists():
            print("❌ Nenhum G-code disponível para teste")
            print("\nArquivos disponíveis em data/output/:")
            for f in Path("data/output").glob("*.gcode"):
                print(f"  - {f.name}")
            return False
    
    print("="*60)
    print("TESTE: Abertura Nativa de G-code")
    print("="*60)
    print(f"\nArquivo: {gcode_path.name}")
    print(f"Tamanho: {gcode_path.stat().st_size / 1024:.1f} KB")
    
    print("\n[1/2] Abrindo G-code com aplicação padrão...")
    print("⏳ Aguarde o Creality Print abrir...")
    
    try:
        # Windows abre com aplicação padrão (caminho absoluto)
        subprocess.Popen([str(gcode_path.absolute())], shell=True)
        
        print("\n[2/2] G-code enviado ao Windows")
        print("\n" + "="*60)
        print("AÇÕES MANUAIS NECESSÁRIAS:")
        print("="*60)
        print("1. ✅ Verifique se Creality Print abriu automaticamente")
        print("2. ✅ Verifique se o modelo aparece no preview 3D")
        print("3. ✅ Verifique se o botão 'Print/Send' está disponível")
        print("\n✅ Se tudo acima funcionar: G-code NATIVO confirmado")
        print("❌ Se não abrir: precisamos ajustar estratégia")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_native_gcode_open()
    
    print("\n" + "="*60)
    input("⏸ Pressione ENTER após validar no Creality Print...")
    
    if success:
        print("\n📋 PRÓXIMO PASSO:")
        print("   Se G-code abriu nativamente:")
        print("   → Pipeline simplificado viável")
        print("   → Elimina parte da GUI automation")
        print("\n   Se G-code NÃO abriu:")
        print("   → Mantém GUI automation atual (STL→Slice→Send)")