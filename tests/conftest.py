# tests/conftest.py
"""
Configuração pytest
"""
import sys
from pathlib import Path

# Adicionar src/ ao PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

print(f"[conftest.py] Adicionado ao path: {project_root / 'src'}")