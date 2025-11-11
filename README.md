# 🖨️ K1 Max Controller

Biblioteca Python para controle da impressora 3D Creality K1 Max integrada com API Metaverso UFG.

## 🎯 Sobre o Projeto
Sistema de controle e monitoramento para impressoras Creality K1 Max, oferecendo interface programática via WebSocket e automação CLI/GUI, integrado ao ecossistema Metaverso UFG.

## ✨ Funcionalidades

### 🖨️ Controle K1 Max
5 funções de controle implementadas:

1. `is_printing()` - Verifica se está imprimindo (WebSocket)
2. `is_ready()` - Verifica se está livre e pronta (WebSocket)
3. `set_material(material)` - Valida e prepara configuração de material
4. `set_temperature(nozzle, bed)` - Valida temperaturas para aplicação
5. `send_print_job(file)` - Envia arquivo para impressão (aplica configs 3-4)

**Nota Técnica:** Funções 1-2 leem estado via WebSocket em tempo real. Funções 3-4 validam parâmetros aplicados durante `send_print_job()` via GUI automation (WebSocket K1 Max é read-only).

### 🌐 Integração API Metaverso

✅ Autenticação automática  
✅ Gerenciamento de fila de impressão  
✅ Sincronização de status  
✅ 8 métodos disponíveis

### 📊 Monitoramento WebSocket

✅ Telemetria em tempo real  
✅ Status de impressão  
✅ Temperaturas (nozzle/bed)  
✅ Progresso e layers

## 🛠️ Tecnologias

- **Python 3.13+**: Linguagem principal
- **Slic3r 1.3.0**: Slicer CLI para G-code generation
- **WebSocket**: Protocolo tempo real (porta 9999)
- **Trimesh**: Processamento GLB→STL com correção automática
- **Requests**: Cliente HTTP
- **PyYAML**: Gerenciamento configuração
- **Pytest**: Framework de testes

## 📋 Pré-requisitos

### Software
```bash
python --version  # 3.13+
```

**Slic3r 1.3.0:**
- Download: https://dl.slic3r.org/win/Slic3r-1.3.0.64bit.zip
- Extrair em: `C:\Slic3r\` ou local preferido

**Creality Print 6.2:**
- `C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe`

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

### Workflow Completo
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

## 🚀 Pipeline Automatizado (NEW!)

### ✅ 95% Automação Atingida
- **Latência:** 90s → 42s (slice time)
- **Taxa sucesso:** 100% (validado em produção)
- **G-code generation:** Slic3r CLI (sem GUI)

```python
from src.converters.glb_to_stl import convert_glb_to_stl

# Conversão automática com 3 níveis de correção:
# 1. Escala metros→milímetros (1000x)
# 2. Redimensionamento para caber na mesa (280mm)
# 3. Centralização e posicionamento (150,150,0)

stl_path = convert_glb_to_stl("model.glb")
```

### Pipeline CLI Completo
```bash
python test_simplified_pipeline.py
```

**Fluxo:**
1. GLB→STL (Trimesh + correções automáticas)
2. STL→G-code (Slic3r CLI + perfil K1 Max)
3. Preview automático (Creality Print)
4. Send manual (clique "Enviar impressão")

### Modelos Validados
✅ `sf-1_white_ghost__futuristic_starfighter.glb` (21MB G-code, 15h28min)  
✅ Geometrias complexas + escala automática  
✅ Posicionamento correto (150,150) na mesa 300x300mm

### Preset Slic3r K1 Max
- **Bed size:** 300x300mm
- **Nozzle:** 0.4mm
- **Filament:** 1.75mm PLA
- **Layer height:** 0.3mm
- **Infill:** 20% stars pattern
- **Temperatures:** 220°C nozzle, 60°C bed

## 📁 Estrutura

```
metaversoufg-printerinterface/
├── src/
│   ├── k1max/
│   │   ├── controller.py         # 5 funções principais
│   │   └── monitor.py            # WebSocket monitor
│   ├── converters/
│   │   └── glb_to_stl.py         # Conversão automática (NEW!)
│   └── adapters/
│       └── metaverso_client.py   # API Metaverso
├── tests/
│   ├── unit/                     # 8 testes unitários
│   ├── integration/              # Testes integração
│   └── test_simplified_pipeline.py # Pipeline CLI (NEW!)
├── config/
│   ├── config.yaml               # Config (gitignored)
│   ├── slic3r_k1max.ini          # Perfil Slic3r (NEW!)
│   └── config.example.yaml       # Template
├── models/                       # Arquivos 3D (.glb, .stl)
├── data/output/                  # G-code gerado
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

**Campos críticos:**
- `state`: 0=idle, 1=printing
- `printProgress`: 0-100%
- `nozzleTemp`, `bedTemp0`: Temperaturas (string)
- `printFileName`: Arquivo atual (material no nome: PLA)

**Limitação:** Protocolo é read-only. Comandos de escrita não descobertos via engenharia reversa. HTTP upload testado (erro 500). GUI automation necessária para comandos.

## 🧪 Testes

```bash
# Testes unitários (8/8 passing)
pytest tests/unit/ -v

# Teste API Metaverso
python test_integration_api.py

# Pipeline completo (requer hardware)
python test_simplified_pipeline.py
```

## 📈 Status Atualizado

| Componente | Status | Performance |
|------------|--------|-------------|
| K1 Max Controller | ✅ | 8/8 tests |
| GLB→STL Converter | ✅ | 3-level auto-correction |
| Slic3r CLI | ✅ | 42s slice time |
| API Metaverso | ✅ | 17 objects in queue |
| WebSocket Monitor | ✅ | Real-time |
| **Pipeline Completo** | **✅ 95%** | **Validated** |

### 🎯 SISTEMA 95% COMPLETO

| Função | Método | Testado |
|--------|--------|---------|
| `is_printing()` | WebSocket (read) | ✅ Lab |
| `is_ready()` | WebSocket (read) | ✅ Lab |
| `set_material()` | Validação + Preset | ✅ |
| `set_temperature()` | Validação + Preset | ✅ |
| `send_print_job()` | Slic3r CLI + GUI | ✅ |

**⚠️ Pendência:** MinIO acesso externo (`metaversoufg-minio:9000`)

## ⚠️ Limitações Conhecidas

### MinIO Inacessível
- **URLs internas:** `metaversoufg-minio:9000`
- **Erro:** Name Resolution Error (rede UFG interna)
- **Workaround:** Aguardando liberação acesso externo
- **Impact:** Fila API funcional, mas download GLB bloqueado

### WebSocket Read-Only
- **K1 Max:** Protocolo proprietário (apenas telemetria)
- **Solução:** Slic3r CLI (95%) + GUI automation (5%)
- **Performance:** 42s slice vs 90s+ anteriormente

## 🔧 Troubleshooting

### WebSocket Timeout
```
Error: timed out during opening handshake
```
✅ Verificar IP em `config.yaml` e impressora ligada

### Slic3r CLI Not Found
```
FileNotFoundError: Slic3r-console.exe
```
✅ Instalar Slic3r 1.3.0 e atualizar path em `test_simplified_pipeline.py`

### Autenticação API
```
401 Unauthorized
```
✅ Atualizar credenciais em `config.yaml`

## 📝 Changelog

### v3.0.0 (2025-11-10)

🚀 **MAJOR RELEASE - 95% Pipeline Automation**

✅ **Slic3r CLI Integration** - Eliminado 95% GUI dependency  
✅ **GLB→STL Converter** - 3-level auto-correction (scale, resize, position)  
✅ **Automated Pipeline** - GLB→G-code em 42s  
✅ **K1 Max Profile** - Perfil validado (300x300mm bed)  
✅ **Production Ready** - 100% success rate em testes  

**Breaking Changes:**
- PrusaSlicer removido (bug CLI)
- Slic3r 1.3.0 agora obrigatório

### v2.0.0 (2025-10-16)

✅ Implementa 5 funções (controller, monitor)  
✅ WebSocket protocol descoberto via engenharia reversa (read-only)  
✅ Integração API Metaverso (8 métodos)  
✅ 8 testes unitários (100% passing)  
🔧 Reorganização estrutura (`src/`, `tests/`, `docs/`)

### v1.0.0

✨ Implementação inicial GUI automation  
✨ Integração Creality Print

## 👥 Autores
**Yan Santos** - Desenvolvimento - [GitLab](https://gitlab.com/ivato)

## 📞 Contato

- **Repositório:** [metaversoufg-printerinterface](https://gitlab.com/ivato/immersion/metaversoufg-printerinterface)
- **Email:** leiteyan@discente.ufg.br

## 📄 Licença
MIT License - veja LICENSE

---

*Desenvolvido para o Metaverso UFG* 🎓
