# Metaverso UFG - Printer Interface

Pipeline automatizado: Metaverso VR → Impressora 3D

## Instalação
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Uso
```bash
python pipeline.py [caminho_glb]
```

## Estrutura

- `pipeline.py` - Entry point principal
- `src/automation/` - Pipeline e GUI automation
- `src/converters/` - Conversão GLB→STL
- `src/slicer/` - PrusaSlicer CLI wrapper
- `data/` - Dados de entrada/saída

## Fluxo

1. GLB → STL (Trimesh)
2. STL → Creality Print (GUI automation)
3. Slice + Envio → K1 Max
