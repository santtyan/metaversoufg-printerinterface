# 🖨️ Metaverso UFG - Interface de Impressora 3D

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

Sistema automatizado para integração entre o ecossistema Metaverso UFG e impressoras 3D Creality K1 Max, permitindo controle completo via API e automação GUI.

## 🎯 Sobre o Projeto

O **Metaverso UFG - Interface de Impressora 3D** oferece duas interfaces complementares:

- 🔌 **API Client**: Gerenciamento de fila de impressão na nuvem
- 🖨️ **K1 Max Controller**: Controle direto da impressora física
- 🤖 **GUI Automation**: Automação completa do Creality Print
- 📊 **Monitoramento WebSocket**: Status em tempo real da impressora

## ✨ Funcionalidades

### 🌐 Sistema 1: API Metaverso

Menu interativo para gerenciar fila de objetos 3D:

- ✅ Listar objetos disponíveis para impressão
- ✅ Marcar objetos como "imprimindo"
- ✅ Devolver objetos para a fila
- ✅ Autenticação automática com retry

### 🖨️ Sistema 2: Controle K1 Max 

5 funções de controle da impressora:

1. **`is_printing()`** - Verifica se está imprimindo (WebSocket)
2. **`is_ready()`** - Verifica se está livre e pronta (WebSocket)
3. **`set_material(material)`** - Configura tipo de material
4. **`set_temperature(nozzle, bed)`** - Configura temperaturas
5. **`send_print_job(file)`** - Envia arquivo para impressão (workflow completo)

### 🤖 Sistema 3: GUI Automation (Legacy)

Automação completa do Creality Print:

- 📦 Conversão GLB → STL automática
- 🎯 Importação de modelos e presets
- ⚙️ Fatiamento automatizado
- 📤 Envio para impressora com confirmação

## 🛠️ Tecnologias

- **Python 3.13**: Linguagem principal
- **WebSocket**: Comunicação tempo real com impressora
- **PyAutoGUI**: Automação de interface gráfica
- **Trimesh**: Processamento de modelos 3D
- **Requests**: Comunicação com APIs REST
- **PyYAML**: Gerenciamento de configurações

## 📋 Pré-requisitos

### Software
```bash
# Python 3.13 ou superior
python --version

# Creality Print 6.2 instalado em:
C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe
```

### Hardware

- **Impressora**: Creality K1 Max
- **Conexão**: Impressora na mesma rede (porta 9999 para WebSocket)
- **Sistema**: Windows 10/11
- **RAM**: Mínimo 4GB

## 🚀 Instalação

### 1. Clone o Repositório
```bash
git clone https://gitlab.com/ivato/immersion/metaversoufg-printerinterface.git
cd metaversoufg-printerinterface
```

### 2. Crie o Ambiente Virtual
```bash
python -m venv venv_k1max_automation
venv_k1max_automation\Scripts\activate
```

### 3. Instale Dependências
```bash
pip install requests pyautogui trimesh numpy pyyaml websockets
```

### 4. Configure Credenciais

Edite `config/config.yaml`:
```yaml
api:
  base_url: "https://mverso.space"
  auth:
    email: "seu_email@example.com"
    password: "sua_senha"

printer:
  ip: "192.168.20.138"  # IP da sua K1 Max
  port: 9999
```

## 🎮 Uso

### Sistema 1: Menu API 
```bash
# Ativar ambiente virtual
venv_k1max_automation\Scripts\activate

# Executar menu interativo
cd src
python test_menu.py
```

**Menu:**
```
=== METAVERSO UFG - PRINTER API CLIENT ===
1. Listar objetos disponíveis para impressão
2. Marcar objeto como "imprimindo"
3. Devolver objeto para fila
4. Sair
```

---

### Sistema 2: Controle K1 Max 

#### Teste Automatizado
```bash
cd src
python k1max/test_k1max.py
```

#### Uso Programático
```python
from k1max.k1max_controller import K1MaxController

controller = K1MaxController()

# Verificar status
if controller.is_ready():
    print("Impressora pronta!")
    
# Configurar impressão
controller.set_material("PLA")
controller.set_temperature(210, 60)

# Enviar para impressão (workflow completo ~90s)
success = controller.send_print_job('C:/caminho/modelo.glb')
```

---

### Sistema 3: GUI Automation (Legacy)

Chamado automaticamente por `send_print_job()`, mas pode ser executado manualmente:
```bash
cd legacy
python script.py C:/caminho/modelo.glb
```

## 📁 Estrutura do Projeto
```
metaversoufg-printerinterface/
├── 📁 src/                           # Código fonte principal
│   ├── 📁 k1max/                     # Sistema controle K1 Max
│   │   ├── k1max_monitor.py         # Monitor WebSocket
│   │   ├── k1max_controller.py      # Funções 
│   │   └── test_k1max.py            # Testes automatizados
│   ├── 📁 adapters/                  # Adaptadores externos
│   │   └── metaverso_api_client.py  # Cliente API Metaverso
│   └── test_menu.py                  # Menu interativo API
├── 📁 legacy/                        # GUI Automation
│   └── script.py                     # Automação Creality Print
├── 📁 config/                        # Configurações
│   └── config.yaml                   # Credenciais e settings
├── 📁 assets/                        # Assets automação
│   ├── 🖼️ *.png                     # Screenshots botões
│   └── metaverso_PLA.creality_printer # Preset PLA
├── 📁 models/                        # Modelos 3D
│   ├── 📦 *.glb                     # Arquivos GLB
│   └── 🔺 *.stl                     # Arquivos STL
├── 📁 unused/                        # Scripts antigos
└── 📚 README.md                      # Este arquivo
```

## 🔌 APIs e Protocolos

### API Metaverso UFG

#### Autenticação
```http
POST https://mverso.space/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "senha"
}
```

#### Fila de Impressão
```http
GET https://mverso.space/v1/printer/printable?with_file=true
Authorization: Bearer {token}
```

#### Atualização de Status
```http
PATCH https://mverso.space/v1/printer/print/{object_id}
Authorization: Bearer {token}
```

---

### WebSocket K1 Max
```python
# Conexão: ws://{printer_ip}:9999

# Dados recebidos em tempo real:
{
  "state": 0,              # 0=idle, 1=printing
  "nozzleTemp": "210.5",   # Temperatura bico
  "bedTemp": "60.0",       # Temperatura mesa
  "printSpeed": "100",     # Velocidade
  "progress": "0"          # Progresso 0-100
}
```

## 📊 Exemplos de Uso

### Exemplo 1: Workflow Completo Automatizado
```python
from src.adapters.metaverso_api_client import MetaversoAPIClient
from src.k1max.k1max_controller import K1MaxController
import base64
import time

# Inicializar clientes
api = MetaversoAPIClient()
controller = K1MaxController()

# 1. Autenticar
api.authenticate()

# 2. Pegar primeiro objeto da fila
objetos = api.get_printable_objects()
if objetos:
    obj = objetos[0]
    obj_id = obj["object_id"]
    
    # 3. Verificar se impressora está pronta
    if controller.is_ready():
        # 4. Salvar arquivo
        arquivo = base64.b64decode(obj["object_file"])
        with open(f"models/{obj_id}.glb", "wb") as f:
            f.write(arquivo)
        
        # 5. Marcar como imprimindo na API
        api.mark_object_printing(obj_id)
        
        # 6. Enviar para impressão
        controller.send_print_job(f"models/{obj_id}.glb")
        
        # 7. Monitorar progresso
        while controller.is_printing():
            time.sleep(10)
            print("Imprimindo...")
        
        # 8. Devolver para fila (ou marcar completo)
        api.mark_object_printable(obj_id)
```

### Exemplo 2: Monitoramento Simples
```python
from src.k1max.k1max_controller import K1MaxController
import time

controller = K1MaxController()

while True:
    if controller.is_printing():
        print("🖨️ Imprimindo...")
    elif controller.is_ready():
        print("✅ Pronta para imprimir")
    else:
        print("⏳ Aquecendo...")
    
    time.sleep(5)
```

## 🔧 Troubleshooting

### Problemas Comuns

#### ❌ WebSocket Timeout
```
Error: timed out during opening handshake
```
**Solução**: Verifique se impressora está ligada e IP correto em `config.yaml`

#### ❌ Botão Não Clicável
```
ERROR: Elemento 'slice_button.png' não encontrado
```
**Solução**: 
1. Recapture screenshot do botão após fatiamento
2. Reduza `confidence` no `script.py`
3. Aguarde mais tempo (`time.sleep`)

#### ❌ Erro de Autenticação API
```
401 Unauthorized
```
**Solução**: Atualize credenciais em `config/config.yaml`

#### ❌ Path Relativo Não Encontrado
```
FileNotFoundError: '../models/file.glb'
```
**Solução**: Use path absoluto: `C:/Projetos/.../models/file.glb`

### Debug Avançado
```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Testes

### Testar Sistema Completo
```bash
cd src
python k1max/test_k1max.py
```

### Testar API Isoladamente
```bash
cd src
python test_menu.py
```

### Testar GUI Automation
```bash
cd legacy
python script.py C:/path/to/test.glb
```

## 📈 Status das Implementações

| Componente | Status | Testado |
|------------|--------|---------|
| API Client | ✅ Completo | ✅ Sim |
| WebSocket Monitor | ✅ Completo | ⏳ Aguarda hardware |
| is_printing() | ✅ Completo | ⏳ Aguarda hardware |
| is_ready() | ✅ Completo | ⏳ Aguarda hardware |
| set_material() | ✅ Completo | ✅ Sim |
| set_temperature() | ✅ Completo | ✅ Sim |
| send_print_job() | ✅ Completo | ✅ Sim |
| GUI Automation | ✅ Completo | ✅ Sim |

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Changelog

### v2.0.0 (2025-10-15)
- ➕ Sistema controle K1 Max 
- ➕ Cliente API Metaverso 
- ➕ Monitor WebSocket tempo real
- 🔧 Reorganização estrutura (src/, legacy/, config/)
- 🔧 Script.py aceita argumentos via subprocess
- 🐛 Correção duplo clique botões Fatiar/Enviar

### v1.0.0 (Anterior)
- ✨ Implementação inicial GUI automation
- ✨ Conversão GLB → STL
- ✨ Integração Creality Print

## 👥 Autores

- **Yan Santos** - *Desenvolvimento* - [GitHub](https://github.com/santtyan)

## 📞 Contato

- **GitLab**: [metaversoufg-printerinterface](https://gitlab.com/ivato/immersion/metaversoufg-printerinterface)
- **Email**: leiteyan@discente.ufg.br

## 📄 Licença

Este projeto está sob licença MIT - veja arquivo LICENSE para detalhes.

---

**Desenvolvido para o Metaverso UFG** 🎓