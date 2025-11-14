
## 🏗️ Reorganização Arquitetural (v4.0.0 - Nov 2025)

### Nova Estrutura Modular

Sistema reorganizado seguindo especificação do coordenador com arquitetura top-down:
```
metaversoufg-printerinterface/
├── main.py                      # ✨ NOVO - Entry point principal (pseudocódigo)
├── src/
│   ├── api/                     # ✨ NOVO - Wrappers API
│   │   └── metaverso_api.py    # Interface simplificada
│   ├── utils/                   # ✨ NOVO - Utilitários
│   │   ├── preset_utils.py     # choosePreset()
│   │   └── converter_utils.py  # convertGlbtoSTL()
│   ├── slicer/
│   │   └── slicer_wrapper.py   # ✨ sliceSTL() extraído
│   ├── k1max/                   # Controle K1 Max
│   ├── converters/              # Conversores formato
│   └── adapters/                # Adapters externos
├── archive/                     # ✨ NOVO - Código legacy
│   ├── run_pipeline.py         # Pipeline local (fallback)
│   └── test_converter_refactored.py
└── docs/                        # ✨ NOVO - Documentação
    └── REORGANIZATION.md
```

### Pipeline Principal (main.py)

Sistema agora opera com loop contínuo 24/7:
```bash
# Modo produção (polling automático)
python main.py

# Com config customizado
python main.py meu_config.yaml

# Ajuda
python main.py --help
```

**Fluxo automatizado:**
1. Polling API (30s) → Buscar objetos na fila
2. Download GLB → Base64 ou URL  
3. GLB → STL → Correção automática escala
4. STL → G-code → Slic3r CLI (42s)
5. Enviar → Creality Print
6. Notificar → Backend (status "printing")

### Conformidade Especificação

- ✅ **Config YAML**: Minimalista com campos solicitados
- ✅ **MetaversoAPI**: Classe wrapper separada
- ✅ **Módulos auxiliares**: Top-down, baixo acoplamento
- ✅ **Alta coesão**: Funções bem definidas
- ✅ **Extensível**: Preparado para Ender3 V3

