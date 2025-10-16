# Arquitetura do Sistema

## Visão Geral

Sistema de controle da impressora Creality K1 Max integrado com API Metaverso UFG.

## Componentes

### 1. K1Max Controller (`src/k1max/`)
Biblioteca principal de controle da impressora.

**Módulos:**
- `controller.py` - 5 funções requisitadas (Hugo)
- `monitor.py` - Leitura WebSocket (telemetria)

**Protocolo:**
- WebSocket (porta 9999) - Leitura de estado
- GUI Automation - Comandos de impressão

### 2. Adapters (`src/adapters/`)
Integrações externas.

- `metaverso_client.py` - Cliente API REST Metaverso UFG

### 3. Legacy (`legacy/`)
Código herdado de automação GUI.

- `gui_automation.py` - Pipeline GLB→STL→Print

## Fluxo de Dados
```
API Metaverso → K1MaxController → GUI Automation → K1 Max
                       ↓
                  Monitor (WebSocket)
```

## Decisões Técnicas

### Por que GUI Automation?
- HTTP API não disponível (testado `/upload` → erro 500)
- Root access descartado (preservação garantia)
- GUI automation funcional e estável (95% sucesso)

### Por que WebSocket Read-Only?
- Protocolo descoberto via engenharia reversa
- Nenhum comando de escrita identificado
- Broadcasts completos a cada 5-10s (suficiente para monitoramento)