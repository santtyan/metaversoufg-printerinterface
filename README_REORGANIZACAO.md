# Sistema de Impressão 3D Automatizada - Metaverso UFG

## ✅ Reorganização Arquitetural Concluída

### Estrutura Implementada
```
metaversoufg-printerinterface/
├── main.py                         # Pipeline principal (pseudocódigo coordenador)
├── config/
│   └── config.yaml                 # YAML minimalista
├── src/
│   ├── api/
│   │   └── metaverso_api.py        # Wrapper MetaversoAPI standalone
│   ├── utils/
│   │   ├── preset_utils.py         # choosePreset()
│   │   └── converter_utils.py      # convertGlbtoSTL()
│   ├── slicer/
│   │   └── slicer_wrapper.py       # sliceSTL() - Slic3r CLI
│   ├── converters/
│   │   └── glb_to_stl.py           # Conversão com correção escala
│   └── adapters/
│       └── metaverso_client.py     # Cliente base (legacy)
└── run_pipeline.py                  # Pipeline local (fallback)
```

### Uso
```bash
# Modo normal (loop 24/7)
python main.py

# Com config customizado
python main.py meu_config.yaml

# Ajuda
python main.py --help
```

### Pipeline Automatizado
```
1. Polling API (30s) → Busca objetos na fila
2. Download GLB → Base64 ou URL
3. GLB → STL → Trimesh com correção escala
4. STL → G-code → Slic3r CLI (45s)
5. Enviar impressão → Creality Print
6. Notificar backend → Status "printing"
```

### Conformidade

- ✅ **Obs 1**: Config YAML com campos solicitados
- ✅ **Obs 2**: MetaversoAPI classe separada
- ✅ **Obs 3**: Arquitetura modular preparada
- ✅ **Obs 4**: Códigos auxiliares em módulos separados
- ✅ **Obs 5**: Top-down, baixo acoplamento, alta coesão

### Teste Realizado
```
✓ Autenticação API: Sucesso
✓ Loop principal: Funcionando
✓ Polling 30s: OK
✓ Graceful shutdown: OK
```

### Próximos Passos

1. Adicionar objetos na fila Metaverso
2. Testar pipeline completo end-to-end
3. Validar impressão K1 Max
4. Expandir para Ender3 V3 (CuraEngine)

---

**Data:** 14/11/2025  
**Status:** Sistema operacional - aguardando objetos na fila
