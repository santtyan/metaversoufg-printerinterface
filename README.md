🖨️ K1 Max Controller

Biblioteca Python para controle da impressora 3D Creality K1 Max integrada com API Metaverso UFG.

🎯 Sobre o Projeto
Sistema de controle e monitoramento para impressoras Creality K1 Max, oferecendo interface programática via WebSocket e GUI automation, integrado ao ecossistema Metaverso UFG.

✨ Funcionalidades

🖨️ Controle K1 Max
5 funções de controle implementadas:

- is_printing() - Verifica se está imprimindo (WebSocket)
- is_ready() - Verifica se está livre e pronta (WebSocket)
- set_material(material) - Valida e prepara configuração de material
- set_temperature(nozzle, bed) - Valida temperaturas para aplicação
- send_print_job(file) - Envia arquivo para impressão (aplica configs 3-4)

Nota Técnica: Funções 1-2 leem estado via WebSocket em tempo real. Funções 3-4 validam parâmetros aplicados durante send_print_job() via GUI automation (WebSocket K1 Max é read-only).

🌐 Integração API Metaverso

✅ Autenticação automática
✅ Gerenciamento de fila de impressão  
✅ Sincronização de status
✅ 8 métodos disponíveis

📊 Monitoramento WebSocket

✅ Telemetria em tempo real
✅ Status de impressão
✅ Temperaturas (nozzle/bed)
✅ Progresso e layers

🛠️ Tecnologias

- Python 3.13+: Linguagem principal
- WebSocket: Protocolo tempo real (porta 9999)
- PyAutoGUI: Automação GUI
- Trimesh: Processamento 3D
- Requests: Cliente HTTP
- PyYAML: Gerenciamento configuração
- Pytest: Framework de testes

📋 Pré-requisitos

Software
```bash
python --version  # 3.13+
```

Creality Print 6.2:
```
C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe
```

Hardware
- Creality K1 Max na rede
- Windows 10/11
- RAM mínima: 4GB

🚀 Instalação

Via pip (recomendado)
```bash
git clone https://gitlab.com/ivato/immersion/metaversoufg-printerinterface.git
cd metaversoufg-printerinterface
pip install -e .
```

Manual
```bash
python -m venv venv_k1max_automation
venv_k1max_automation\Scripts\activate
pip install -r requirements.txt
```

Configuração
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

🎮 Uso

Exemplo Básico
```python
from k1max.controller import K1MaxController

controller = K1MaxController()

# Verificar disponibilidade
if controller.is_ready():
    # Preparar configurações
    controller.set_material('PLA')
    controller.set_temperature(210, 60)
    
    # Enviar arquivo (aplica configurações)
    controller.send_print_job('models/object.glb')
```

Workflow Completo
```python
from adapters.metaverso_client import MetaversoAPIClient
from k1max.controller import K1MaxController

# Integração API + Impressora
api = MetaversoAPIClient()
controller = K1MaxController()

api.authenticate()
objetos = api.get_printable_objects()

if objetos and controller.is_ready():
    obj = objetos[0]
    api.mark_object_printing(obj['object_id'])
    api.save_object_file(obj['object_id'], 'models/temp.glb')
    controller.send_print_job('models/temp.glb')
```

## 🚀 PrusaSlicer CLI Integration (NEW!)

### Pipeline Otimizado
✅ **95% redução GUI automation**  
✅ **Latência: 90s → <1s** (90x melhoria)  
✅ **Taxa sucesso: 100%** (6/6 modelos testados)
```python
from src.slicer.prusa_slicer_wrapper import slice_with_creality_presets

# Slice direto com presets Creality
gcode_path = slice_with_creality_presets("model.stl", "PLA")
```

### Modelos Validados
- ✅ obj_1_Double_grip_01.stl (2.9MB G-code)
- ✅ obj_1_飞龙.stl (3.9MB G-code) 
- ✅ obj_1_dbz_standing_hero.stl (13.8MB G-code)
- ✅ obj_1_ana_avrat_siken_super_man.stl (9.6MB G-code)
- ✅ Geometrias complexas + caracteres especiais

### Preset Metaverso
- **Suportes**: Tree automáticos
- **Infill**: 10% honeycomb  
- **Brim**: 8mm outer-only
- **Temperaturas**: 220°C nozzle, 60°C bed

📁 Estrutura
```
metaversoufg-printerinterface/
├── src/
│   ├── k1max/
│   │   ├── controller.py         # 5 funções principais
│   │   └── monitor.py            # WebSocket monitor
│   ├── slicer/
│   │   └── prusa_slicer_wrapper.py # PrusaSlicer CLI (NEW!)
│   ├── presets/
│   │   └── creality_preset_parser.py # Parser presets (NEW!)
│   └── adapters/
│       └── metaverso_client.py   # API Metaverso
├── tests/
│   ├── unit/                     # 8 testes unitários
│   ├── integration/              # Testes integração
│   └── discovery/                # Testes protocolo
├── config/
│   ├── config.yaml               # Config (gitignored)
│   └── config.example.yaml       # Template
├── docs/                         # Documentação técnica
├── research/                     # Engenharia reversa (arquivado)
├── assets/                       # Screenshots GUI automation
├── models/                       # Arquivos 3D
├── setup.py
└── README.md
```

🔌 Protocolo WebSocket K1 Max

Conexão
```
ws://192.168.20.175:9999
ping_interval=None  # CRÍTICO: K1 Max não responde PING frames
```

Broadcast Completo (~5-10s)
```json
{
  "state": 0,
  "printProgress": 0,
  "nozzleTemp": "25.0",
  "bedTemp0": "24.0",
  "printFileName": "/path/file.gcode"
}
```

Campos críticos:
- state: 0=idle, 1=printing
- printProgress: 0-100%
- nozzleTemp, bedTemp0: Temperaturas (string)
- printFileName: Arquivo atual (material no nome: _PLA_)

Limitação: Protocolo é read-only. Comandos de escrita não descobertos via engenharia reversa. HTTP upload testado (erro 500). GUI automation necessária para comandos.

🧪 Testes
```bash
# Testes unitários (8/8 passing)
pytest tests/unit/ -v

# Teste API Metaverso
python test_integration_api.py

# Testes integração (requer hardware)
pytest tests/integration/
```

📈 Status Atualizado

| Componente | Status | Performance |
|------------|--------|-------------|
| K1 Max Controller | ✅ | 8/8 tests |
| **PrusaSlicer CLI** | ✅ | **6/6 models** |
| API Metaverso | ✅ | **17 objects in queue** |
| WebSocket Monitor | ✅ | Real-time |
| **Pipeline Completo** | ✅ | **<1s slice time** |

🎯 **SISTEMA 95% COMPLETO**  
⚠️ **Pendência**: MinIO acesso externo (metaversoufg-minio:9000)

| Função | Método | Testado |
|--------|--------|---------|
| is_printing() | WebSocket (read) | ✅ Lab |
| is_ready() | WebSocket (read) | ✅ Lab |
| set_material() | Validação + Preset | ✅ |
| set_temperature() | Validação + Preset | ✅ |
| send_print_job() | GUI Automation | ✅ |

## ⚠️ Limitações Conhecidas

### MinIO Inacessível
- **URLs internas**: `metaversoufg-minio:9000` 
- **Erro**: Name Resolution Error (rede UFG interna)
- **Workaround**: Aguardando liberação acesso externo
- **Impact**: Fila API funcional, mas download GLB bloqueado

### WebSocket Read-Only
- **K1 Max**: Protocolo proprietário (apenas telemetria)
- **Solução**: GUI automation para comandos de escrita
- **Performance**: 5% dependência GUI (vs 100% anterior)

🔧 Troubleshooting

WebSocket Timeout
```
Error: timed out during opening handshake
```
✅ Verificar IP em config.yaml e impressora ligada

GUI Automation Falha
```
ERROR: Elemento não encontrado
```
✅ Recapturar screenshots em assets/  
✅ Ajustar confidence no código

Autenticação API
```
401 Unauthorized
```
✅ Atualizar credenciais em config.yaml

📚 Documentação
- [Arquitetura](docs/architecture.md)
- [API Reference](docs/api.md)

📝 Changelog

v2.1.0 (2025-11-03)
- ✅ **PrusaSlicer CLI Wrapper** - 95% redução GUI automation
- ✅ **Pipeline otimizado** - 90s → <1s (90x melhoria)
- ✅ **6 modelos validados** - 100% taxa sucesso
- ✅ **Preset Metaverso** - Tree supports, 10% infill, 8mm brim
- ✅ **Fila API integrada** - 17 objetos detectados
- 🔧 **Arquitetura modular** - main.py + config.yaml

v2.0.0 (2025-10-16)
- ✅ Implementa 5 funções (controller, monitor)
- ✅ WebSocket protocol descoberto via engenharia reversa (read-only)
- ✅ Integração API Metaverso (8 métodos)
- ✅ 8 testes unitários (100% passing)
- 🔧 Reorganização estrutura (src/, tests/, docs/)
- 🔧 Discovery HTTP API (não disponível)
- 📚 Documentação técnica completa

v1.0.0
- ✨ Implementação inicial GUI automation
- ✨ Conversão GLB → STL
- ✨ Integração Creality Print

👥 Autores
Yan Santos - Desenvolvimento - GitLab

📞 Contato
- Repositório: metaversoufg-printerinterface
- Email: leiteyan@discente.ufg.br

📄 Licença
MIT License - veja LICENSE

Desenvolvido para o Metaverso UFG 🎓