# 🖨️ K1 Max Controller

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

Biblioteca Python para controle da impressora 3D Creality K1 Max integrada com API Metaverso UFG.

## 🎯 Sobre o Projeto

Sistema de controle e monitoramento para impressoras Creality K1 Max, oferecendo interface programática via WebSocket e GUI automation, integrado ao ecossistema Metaverso UFG.

## ✨ Funcionalidades

### 🖨️ Controle K1 Max

5 funções de controle implementadas:

1. **`is_printing()`** - Verifica se está imprimindo (WebSocket)
2. **`is_ready()`** - Verifica se está livre e pronta (WebSocket)
3. **`set_material(material)`** - Configura tipo de material
4. **`set_temperature(nozzle, bed)`** - Configura temperaturas
5. **`send_print_job(file)`** - Envia arquivo para impressão

### 🌐 Integração API Metaverso

- ✅ Autenticação automática com retry
- ✅ Gerenciamento de fila de impressão
- ✅ Sincronização de status

### 📊 Monitoramento WebSocket

- ✅ Telemetria em tempo real
- ✅ Status de impressão
- ✅ Temperaturas (nozzle/bed)
- ✅ Progresso e layers

## 🛠️ Tecnologias

- **Python 3.13+**: Linguagem principal
- **WebSocket**: Protocolo tempo real (porta 9999)
- **PyAutoGUI**: Automação GUI
- **Trimesh**: Processamento 3D
- **Requests**: Cliente HTTP
- **PyYAML**: Gerenciamento configuração

## 📋 Pré-requisitos

### Software
```bash
python --version  # 3.13+
```

**Creality Print 6.2:**
```
C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe
```

### Hardware

- Creality K1 Max na rede
- Windows 10/11
- RAM mínima: 4GB

## 🚀 Instalação

### Via pip (recomendado)
```bash
git clone https://gitlab.com/ivato/immersion/metaversoufg-printerinterface.git
cd metaversoufg-printerinterface
pip install -e .
```

### Manual
```bash
python -m venv venv_k1max_automation
venv_k1max_automation\Scripts\activate
pip install -r requirements.txt
```

### Configuração
```bash
cp config/config.example.yaml config/config.yaml
# Editar config.yaml com suas credenciais
```
```yaml
api:
  base_url: "https://metaverso.medialab.ufg.br/v1"

credentials:
  email: "seu_email@example.com"
  username: "seu_usuario"
  password: "sua_senha"

printer:
  ip: "192.168.20.175"
  websocket_port: 9999
```

## 🎮 Uso

### Exemplo Básico
```python
from src.k1max.k1max_controller import K1MaxController

controller = K1MaxController()

# Verificar disponibilidade
if controller.is_ready():
    # Configurar impressão
    controller.set_material('PLA')
    controller.set_temperature(210, 60)
    
    # Enviar arquivo
    controller.send_print_job('models/object.glb')
```

### Monitoramento
```python
import time

while True:
    if controller.is_printing():
        print("🖨️ Imprimindo...")
    elif controller.is_ready():
        print("✅ Pronta")
    
    time.sleep(5)
```

### Workflow Completo
```python
from src.adapters.metaverso_api_client import MetaversoClient

# Integração API + Impressora
api = MetaversoClient()
controller = K1MaxController()

if api.login():
    queue = api.get_print_queue()
    
    if queue and controller.is_ready():
        obj = queue[0]
        controller.send_print_job(obj['file_path'])
```

## 📁 Estrutura
```
metaversoufg-printerinterface/
├── src/
│   ├── k1max/                    # Controle K1 Max
│   │   ├── k1max_controller.py  # 5 funções principais
│   │   └── k1max_monitor.py     # WebSocket monitor
│   └── adapters/
│       └── metaverso_client.py  # API Metaverso
├── tests/
│   ├── unit/                     # Testes unitários
│   ├── integration/              # Testes integração
│   └── discovery/                # Testes protocolo
├── legacy/
│   └── script.py                 # GUI automation
├── config/
│   ├── config.yaml               # Config (gitignored)
│   └── config.example.yaml       # Template
├── docs/
│   ├── ARCHITECTURE.md           # Arquitetura sistema
│   └── API.md                    # Referência API
├── research/                     # Engenharia reversa (arquivado)
├── setup.py
└── README.md
```

## 🔌 Protocolo WebSocket K1 Max

### Conexão
```python
ws://192.168.20.175:9999
ping_interval=None  # CRÍTICO: K1 Max não responde PING frames
```

### Broadcast Completo (~5-10s)
```json
{
  "state": 0,
  "printProgress": 0,
  "nozzleTemp": "25.0",
  "bedTemp0": "24.0",
  "printFileName": "/path/file.gcode"
}
```

### Update Incremental (~10x/s)
```json
{
  "nozzleTemp": "210.5"
}
```

**Campos críticos:**
- `state`: 0=idle, 1=printing
- `printProgress`: 0-100%
- `nozzleTemp`, `bedTemp0`: Temperaturas (string)
- `printFileName`: Arquivo atual (material no nome: `_PLA_`)

## 🔧 Troubleshooting

### WebSocket Timeout
```
Error: timed out during opening handshake
```
✅ Verificar IP em `config.yaml` e impressora ligada

### GUI Automation Falha
```
ERROR: Elemento não encontrado
```
✅ Recapturar screenshots em `assets/`  
✅ Ajustar `confidence` no código

### Autenticação API
```
401 Unauthorized
```
✅ Atualizar credenciais em `config.yaml`

## 🧪 Testes
```bash
# Teste completo
python -m src.k1max.k1max_controller

# Testes unitários
pytest tests/unit/

# Testes integração (requer hardware)
pytest tests/integration/
```

## 📈 Status

| Função | Status | Método | Testado |
|--------|--------|--------|---------|
| `is_printing()` | ✅ | WebSocket | ✅ Lab |
| `is_ready()` | ✅ | WebSocket | ✅ Lab |
| `set_material()` | ✅ | Preset | ✅ |
| `set_temperature()` | ✅ | Preset | ✅ |
| `send_print_job()` | ✅ | GUI Automation | ✅ |

## 📚 Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)

## 🤝 Contribuição
```bash
git checkout -b feature/nova-funcionalidade
git commit -m "Adiciona funcionalidade X"
git push origin feature/nova-funcionalidade
```

## 📝 Changelog

### v2.0.0 (2025-10-16)
- ✅ Implementa 5 funções Hugo (is_printing, is_ready, set_material, set_temperature, send_print_job)
- ✅ WebSocket monitor com protocolo descoberto via engenharia reversa
- ✅ Integração API Metaverso
- 🔧 Reorganização estrutura (src/, tests/, docs/, research/)
- 🔧 Discovery HTTP API (confirmado não disponível)
- 📚 Documentação técnica completa

### v1.0.0
- ✨ Implementação inicial GUI automation
- ✨ Conversão GLB → STL
- ✨ Integração Creality Print

## 👥 Autores

**Yan Santos** - Desenvolvimento - [GitLab](https://gitlab.com/ivato)

## 📞 Contato

- **Repositório**: [metaversoufg-printerinterface](https://gitlab.com/ivato/immersion/metaversoufg-printerinterface)
- **Email**: leiteyan@discente.ufg.br

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

---

**Desenvolvido para o Metaverso UFG** 🎓