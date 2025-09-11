# 🖨️ Metaverso UFG - Interface de Impressora 3D

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

Uma interface automatizada para integração entre o ecossistema Metaverso UFG e impressoras 3D Creality K1 Max, permitindo impressão automática de objetos 3D diretamente da API do Metaverso.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Características](#características)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API](#api)
- [Troubleshooting](#troubleshooting)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O **Metaverso UFG - Interface de Impressora 3D** é um sistema automatizado que:

- 🔄 **Monitora** a fila de impressão da API do Metaverso UFG
- 📦 **Converte** automaticamente arquivos GLB para STL
- 🖨️ **Automatiza** o processo de impressão no Creality Print
- 📊 **Registra** logs detalhados de todo o processo
- 🔧 **Configura** automaticamente parâmetros de impressão

## ✨ Características

### 🚀 Funcionalidades Principais

- **Integração com API**: Conexão direta com a API do Metaverso UFG
- **Conversão de Formatos**: GLB → STL automática usando Trimesh
- **Automação de UI**: Controle automatizado do Creality Print via PyAutoGUI
- **Modo Teste**: Funcionalidade local para desenvolvimento e testes
- **Logging Centralizado**: Sistema completo de logs para monitoramento
- **Tratamento de Erros**: Gerenciamento robusto de exceções

### 🎮 Automação Completa

1. **Detecção de Objetos**: Monitora fila de impressão da API
2. **Download Automático**: Baixa arquivos 3D da nuvem
3. **Conversão de Formato**: Processa GLB para STL
4. **Configuração de Impressora**: Aplica presets de impressão
5. **Envio para Impressão**: Inicia processo na Creality K1 Max

## 🛠️ Tecnologias

### Linguagens e Frameworks
- **Python 3.8+**: Linguagem principal
- **Requests**: Comunicação com APIs REST
- **PyAutoGUI**: Automação de interface gráfica
- **Trimesh**: Processamento de modelos 3D

### Ferramentas e Serviços
- **Creality Print 6.2**: Software de fatiamento
- **API Metaverso UFG**: Backend do ecossistema
- **Git**: Controle de versão

## 📋 Pré-requisitos

### Software Necessário

```bash
# Python 3.8 ou superior
python --version

# Creality Print 6.2 instalado em:
# C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe
```

### Hardware Compatível

- **Impressora**: Creality K1 Max
- **Sistema**: Windows 10/11
- **RAM**: Mínimo 4GB recomendado
- **Conexão**: Internet para acesso à API

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://gitlab.com/ivato/immersion/metaversoufg-printerinterface.git
cd metaversoufg-printerinterface
```

### 2. Crie um Ambiente Virtual

```bash
python -m venv venv_k1max_automation
venv_k1max_automation\Scripts\activate  # Windows
```

### 3. Instale as Dependências

```bash
pip install requests pyautogui trimesh numpy
```

### 4. Verifique a Instalação

```bash
python script.py --test
```

## ⚙️ Configuração

### 1. Configuração da API

Edite as credenciais no `script.py`:

```python
# Configurações da API
AUTH_URL = "https://mverso.space/v1/auth/login"
AUTH_PAYLOAD = {
    "email": "seu_email@example.com",
    "password": "sua_senha"
}
```

### 2. Configuração de Caminhos

Verifique se os caminhos estão corretos:

```python
# Caminho do Creality Print
SLICER_PATH = r"C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe"

# Pasta do projeto
PROJECT_ROOT = r"C:\Users\USER\Documents\metaversoufg-printerinterface"
```

### 3. Modo de Operação

Para **desenvolvimento/teste**:
```python
USE_LOCAL_FILE = True
LOCAL_FILE_PATH = os.path.join(MODELS_FOLDER, "seu_arquivo_teste.glb")
```

Para **produção**:
```python
USE_LOCAL_FILE = False
```

## 🎮 Uso

### Execução Básica

```bash
# Ativar ambiente virtual
venv_k1max_automation\Scripts\activate

# Executar o script principal
python script.py
```

### Modo Teste Local

1. Coloque um arquivo `.glb` na pasta `models/`
2. Configure `USE_LOCAL_FILE = True`
3. Execute o script

### Modo Produção

1. Configure suas credenciais da API
2. Configure `USE_LOCAL_FILE = False`
3. Execute o script
4. O sistema irá monitorar a fila automaticamente

### Logs de Execução

Os logs são exibidos em tempo real:

```
2025-01-15 10:30:15 - INFO - Tentando autenticar na API do Metaverso...
2025-01-15 10:30:16 - INFO - Autenticação bem-sucedida! Token obtido.
2025-01-15 10:30:17 - INFO - Verificando a fila de impressão da API...
2025-01-15 10:30:18 - INFO - Iniciando conversão de GLB para STL: modelo.glb
2025-01-15 10:30:20 - INFO - Conversão concluída: modelo.stl
```

## 📁 Estrutura do Projeto

```
metaversoufg-printerinterface/
├── 📁 assets/                      # Assets da interface
│   ├── 🖼️ *.png                   # Imagens dos botões do Creality Print
│   └── ⚙️ metaverso_PLA.creality_printer  # Preset de impressão
├── 📁 models/                      # Modelos 3D
│   ├── 📦 *.glb                   # Arquivos GLB baixados
│   ├── 🔺 *.stl                   # Arquivos STL convertidos
│   └── 🧪 charmander(1).glb       # Arquivo de teste
├── 🐍 script.py                   # Script principal
├── ⚙️ config.py                   # Configurações
├── 🧪 test_*.py                   # Scripts de teste
├── 📚 README.md                   # Este arquivo
└── 📄 requirements.txt            # Dependências Python
```

## 🔗 API

### Endpoints Utilizados

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

### Formato de Dados

```json
{
  "object_id": "uuid-do-objeto",
  "object_file": "base64-encoded-glb-file",
  "created_at": "2025-01-15T10:30:00Z"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### ❌ Erro de Autenticação
```
Erro fatal de autenticação: 401 Unauthorized
```
**Solução**: Verifique suas credenciais no `script.py`

#### ❌ Creality Print não encontrado
```
Erro: Slicer não encontrado em 'C:\Program Files\...'
```
**Solução**: Atualize o caminho `SLICER_PATH` no script

#### ❌ Erro de conversão GLB→STL
```
Erro na conversão de GLB para STL: [...]
```
**Solução**: Verifique se o arquivo GLB não está corrompido

#### ❌ Elementos da UI não encontrados
```
Erro: Elemento 'botão.png' não encontrado na tela
```
**Solução**: 
1. Verifique se o Creality Print está aberto
2. Capture novos screenshots dos botões se necessário
3. Ajuste os valores de `confidence` no código

### Logs Detalhados

Para debug avançado, altere o nível de log:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Suporte

Para suporte técnico:
- 📧 Email: suporte@metaversoufg.com
- 🐛 Issues: [GitLab Issues](https://gitlab.com/ivato/immersion/metaversoufg-printerinterface/-/issues)
- 📖 Wiki: [Documentação Completa](https://gitlab.com/ivato/immersion/metaversoufg-printerinterface/-/wikis/home)

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Diretrizes de Contribuição

- 📝 Siga o padrão de código existente
- ✅ Adicione testes para novas funcionalidades
- 📚 Atualize a documentação quando necessário
- 🔍 Teste localmente antes de submeter

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 👥 Autores

- **Equipe Metaverso UFG** - *Desenvolvimento inicial* - [UFG](https://github.com/metaversoufg)

## 📞 Contato

- **Projeto**: [https://gitlab.com/ivato/immersion/metaversoufg-printerinterface](https://gitlab.com/ivato/immersion/metaversoufg-printerinterface)
- **Website**: [https://metaversoufg.com](https://metaversoufg.com)
- **Email**: contato@metaversoufg.com

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela!**

*Desenvolvido com ❤️ pela equipe Metaverso UFG*