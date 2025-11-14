#!/usr/bin/env python3
"""
Pipeline Principal: Metaverso UFG -> Impressao 3D
Uso: python pipeline.py [caminho_glb]
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from automation.pipeline import main

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
