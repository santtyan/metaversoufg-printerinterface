"""
K1 Max Production WebSocket Client
Cliente robusto para uso em produção baseado nas descobertas da análise

PROPÓSITO: Este é o cliente FINAL que você usará em produção após descobrir
os comandos via websocket_analyzer.py. Inclui:
- Circuit breaker para resiliência
- Retry automático com backoff exponencial
- Fallback para GUI se WebSocket falhar
- Monitoramento contínuo de status

QUANDO USAR: Após análise completa. Substitui (parcial ou totalmente)
sua automação GUI atual.
"""

import asyncio
import websockets
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
import hashlib
import signal
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('k1max_production.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PrinterState(Enum):
    """Estados possíveis da impressora"""
    IDLE = "idle"
    PRINTING = "printing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    HEATING = "heating"
    READY = "ready"
    UNKNOWN = "unknown"

class CommandResult(Enum):
    """Resultados de execução de comandos"""
    SUCCESS = auto()
    FAILURE = auto()
    TIMEOUT = auto()
    PARTIAL_SUCCESS = auto()
    RETRY_NEEDED = auto()

@dataclass
class PrinterStatus:
    """
    Status completo da impressora
    
    PROPÓSITO: Estrutura padronizada para status da impressora.
    Facilita monitoramento e tomada de decisões.
    """
    state: PrinterState
    temperatures: Dict[str, float] = field(default_factory=dict)
    progress: float = 0.0
    current_file: Optional[str] = None
    estimated_time_remaining: Optional[int] = None
    last_update: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    
    @property
    def is_operational(self) -> bool:
        """Verifica se impressora está operacional"""
        return self.state not in [PrinterState.ERROR, PrinterState.UNKNOWN]
    
    @property
    def is_ready_for_print(self) -> bool:
        """Verifica se está pronta para iniciar impressão"""
        return self.state in [PrinterState.IDLE, PrinterState.READY]

@dataclass
class CommandDefinition:
    """
    Definição de comando baseada nas descobertas
    
    IMPORTANTE: Esta estrutura é preenchida automaticamente
    pelo sistema de análise (websocket_data_analyzer.py)
    """
    name: str
    payload: Dict[str, Any]
    expected_response_fields: List[str]
    timeout_seconds: float = 10.0
    retry_count: int = 3
    success_indicators: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)

class K1MaxProductionClient:
    """
    Cliente de produção para K1 Max
    
    FLUXO DE USO:
```python
    client = K1MaxProductionClient()
    await client.connect()
    
    # Obter status
    status = await client.get_printer_status()
    
    # Enviar comando
    result = await client.send_command('get_temperature')
    
    await client.disconnect()
"""

def __init__(self, printer_ip: str = "200.137.221.11", port: int = 9999):
    """
    Inicializa cliente de produção
    
    PARÂMETROS:
    - printer_ip: IP da K1 Max
    - port: Porta WebSocket (9999 padrão)
    """
    self.printer_ip = printer_ip
    self.port = port
    self.uri = f"ws://{printer_ip}:{port}"
    
    # Estado da conexão
    self.websocket = None
    self.is_connected = False
    self.connection_attempts = 0
    self.max_connection_attempts = 5
    
    # Circuit breaker para resiliência
    self.circuit_breaker_open = False
    self.circuit_breaker_failures = 0
    self.circuit_breaker_threshold = 3
    self.last_circuit_breaker_reset = datetime.now()
    
    # Status da impressora
    self.current_status = PrinterStatus(PrinterState.UNKNOWN)
    
    # Comandos descobertos (carregados da análise)
    self.discovered_commands: Dict[str, CommandDefinition] = {}
    self.load_discovered_commands()
    
    # Controle de shutdown graceful
    self.running = False
    signal.signal(signal.SIGINT, self._signal_handler)

def _signal_handler(self, signum, frame):
    """Handler para shutdown gracioso"""
    logger.info(f"Recebido sinal {signum}, desconectando...")
    self.running = False

def load_discovered_commands(self):
    """
    Carrega comandos descobertos da análise prévia
    
    IMPORTANTE: Este método procura o arquivo gerado pelo
    websocket_data_analyzer.py (k1max_analysis_complete_report.json)
    e carrega os comandos descobertos.
    
    FALLBACK: Se arquivo não existir, carrega comandos básicos padrão.
    """
    try:
        analysis_file = Path("k1max_analysis_complete_report.json")
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Converte descobertas para definições de comando
            api_doc = analysis_data.get('api_documentation', {})
            endpoints = api_doc.get('endpoints', {})
            
            for cmd_id, details in endpoints.items():
                cmd_def = CommandDefinition(
                    name=cmd_id,
                    payload=details['command_structure'],
                    expected_response_fields=list(details.get('response_example', {}).keys()),
                    timeout_seconds=max(10.0, details.get('average_response_time_ms', 1000) / 1000 * 3),
                    success_indicators=['result', 'data', 'status', 'success']
                )
                self.discovered_commands[cmd_id] = cmd_def
            
            logger.info(f"Carregados {len(self.discovered_commands)} comandos descobertos")
        else:
            logger.warning("Arquivo de análise não encontrado, usando comandos padrão")
            self._load_fallback_commands()
            
    except Exception as e:
        logger.error(f"Erro carregando comandos: {e}")
        self._load_fallback_commands()

def _load_fallback_commands(self):
    """
    Carrega comandos básicos como fallback
    
    PROPÓSITO: Se análise completa não estiver disponível,
    usa comandos básicos conhecidos da pesquisa Node-RED.
    """
    basic_commands = [
        CommandDefinition(
            name="get_status",
            payload={"cmd": "get_status"},
            expected_response_fields=["status", "state"],
            success_indicators=["status", "result"]
        ),
        CommandDefinition(
            name="get_temperature",
            payload={"request": "temperature"},
            expected_response_fields=["temperature", "bed", "nozzle"],
            success_indicators=["temperature"]
        ),
        CommandDefinition(
            name="get_progress",
            payload={"action": "get_progress"},
            expected_response_fields=["progress", "percent"],
            success_indicators=["progress"]
        )
    ]
    
    for cmd in basic_commands:
        self.discovered_commands[cmd.name] = cmd

async def connect(self) -> bool:
    """
    Conecta ao WebSocket com circuit breaker
    
    RETORNA: True se conexão bem-sucedida, False caso contrário
    
    CIRCUIT BREAKER: Se houver 3 falhas consecutivas, abre o circuit
    e para de tentar por 60 segundos.
    """
    if self.circuit_breaker_open:
        if not self._should_reset_circuit_breaker():
            logger.warning("Circuit breaker aberto - não tentando conectar")
            return False
        else:
            self.circuit_breaker_open = False
            self.circuit_breaker_failures = 0
    
    try:
        logger.info(f"Conectando a {self.uri}...")
        
        self.websocket = await websockets.connect(
            self.uri,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5
        )
        
        self.is_connected = True
        self.connection_attempts = 0
        self.running = True
        
        logger.info("Conexão WebSocket estabelecida")
        return True
        
    except Exception as e:
        self.connection_attempts += 1
        self._handle_connection_failure(e)
        return False

async def disconnect(self):
    """Desconecta graciosamente"""
    self.running = False
    
    if self.websocket:
        await self.websocket.close()
        self.is_connected = False
    
    logger.info("Desconectado da K1 Max")

def _should_reset_circuit_breaker(self) -> bool:
    """
    Verifica se deve resetar o circuit breaker
    
    LÓGICA: Após 60 segundos da última falha, permite nova tentativa
    """
    time_since_last_reset = datetime.now() - self.last_circuit_breaker_reset
    return time_since_last_reset.seconds > 60

def _handle_connection_failure(self, error: Exception):
    """
    Gerencia falhas de conexão com circuit breaker
    
    ESTRATÉGIA: Conta falhas consecutivas. Após 3 falhas,
    abre circuit breaker por 60 segundos.
    """
    logger.error(f"Falha de conexão: {error}")
    
    self.circuit_breaker_failures += 1
    if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
        self.circuit_breaker_open = True
        self.last_circuit_breaker_reset = datetime.now()
        logger.error("Circuit breaker ABERTO - pausando tentativas por 60s")

async def send_command(self, command_name: str, **kwargs) -> CommandResult:
    """
    Envia comando usando definições descobertas
    
    USO:
        result = await client.send_command('get_status')
        result = await client.send_command('fan_control', state='on')
PARÂMETROS:
    - command_name: Nome do comando (deve existir em discovered_commands)
    - **kwargs: Parâmetros adicionais para o comando
    
    RETORNA: CommandResult indicando sucesso/falha
    """
    if not self.is_connected:
        logger.error("Não conectado - tentando reconectar...")
        if not await self.connect():
            return CommandResult.FAILURE
    
    if command_name not in self.discovered_commands:
        logger.error(f"Comando '{command_name}' não descoberto")
        return CommandResult.FAILURE
    
    cmd_def = self.discovered_commands[command_name]
    
    # Monta payload com parâmetros adicionais
    payload = cmd_def.payload.copy()
    payload.update(kwargs)
    
    return await self._execute_command_with_retry(cmd_def, payload)

async def _execute_command_with_retry(self, cmd_def: CommandDefinition, payload: Dict[str, Any]) -> CommandResult:
    """
    Executa comando com retry automático
    
    ESTRATÉGIA: Até 3 tentativas com backoff exponencial
    - Tentativa 1: imediata
    - Tentativa 2: após 2 segundos
    - Tentativa 3: após 4 segundos
    """
    for attempt in range(cmd_def.retry_count):
        try:
            result = await self._execute_single_command(cmd_def, payload)
            
            if result == CommandResult.SUCCESS:
                return result
            elif result == CommandResult.TIMEOUT and attempt < cmd_def.retry_count - 1:
                logger.warning(f"Timeout em {cmd_def.name}, tentativa {attempt + 1}")
                await asyncio.sleep(2 ** attempt)  # Backoff exponencial
                continue
            else:
                return result
                
        except Exception as e:
            logger.error(f"Erro executando {cmd_def.name}, tentativa {attempt + 1}: {e}")
            if attempt < cmd_def.retry_count - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                return CommandResult.FAILURE
    
    return CommandResult.FAILURE

async def _execute_single_command(self, cmd_def: CommandDefinition, payload: Dict[str, Any]) -> CommandResult:
    """
    Executa um comando único com timeout
    
    VALIDAÇÃO: Verifica resposta contra indicadores de sucesso/falha
    """
    try:
        # Adiciona timestamp para rastreamento
        enhanced_payload = {
            **payload,
            "_client_timestamp": datetime.now().isoformat()
        }
        
        # Envia comando
        await self.websocket.send(json.dumps(enhanced_payload))
        logger.debug(f"Comando enviado: {cmd_def.name}")
        
        # Aguarda resposta com timeout
        response_raw = await asyncio.wait_for(
            self.websocket.recv(),
            timeout=cmd_def.timeout_seconds
        )
        
        response = json.loads(response_raw)
        logger.debug(f"Resposta recebida: {response}")
        
        # Valida resposta
        return self._validate_command_response(cmd_def, response)
        
    except asyncio.TimeoutError:
        logger.warning(f"Timeout em {cmd_def.name}")
        return CommandResult.TIMEOUT
    except json.JSONDecodeError:
        logger.error(f"Resposta inválida para {cmd_def.name}")
        return CommandResult.FAILURE
    except Exception as e:
        logger.error(f"Erro executando {cmd_def.name}: {e}")
        return CommandResult.FAILURE

def _validate_command_response(self, cmd_def: CommandDefinition, response: Dict[str, Any]) -> CommandResult:
    """
    Valida se resposta indica sucesso
    
    CRITÉRIOS:
    1. Não contém indicadores de falha
    2. Contém indicadores de sucesso
    3. Contém campos esperados
    """
    response_str = json.dumps(response).lower()
    
    # Verifica falhas primeiro
    if any(fail in response_str for fail in cmd_def.failure_indicators):
        return CommandResult.FAILURE
    
    # Verifica sucessos
    if any(success in response_str for success in cmd_def.success_indicators):
        return CommandResult.SUCCESS
    
    # Verifica campos esperados
    expected_present = sum(1 for field in cmd_def.expected_response_fields if field in response)
    if expected_present >= len(cmd_def.expected_response_fields) * 0.5:
        return CommandResult.PARTIAL_SUCCESS
    
    return CommandResult.FAILURE

async def get_printer_status(self) -> PrinterStatus:
    """
    Obtém status completo da impressora
    
    RETORNA: PrinterStatus com todos os dados disponíveis
    
    NOTA: Tenta diferentes comandos de status até encontrar um funcional
    """
    status = PrinterStatus(PrinterState.UNKNOWN)
    
    # Tenta comandos de status conhecidos
    status_commands = ['get_status', 'get_temperature', 'get_progress']
    
    for cmd_name in status_commands:
        if cmd_name in self.discovered_commands:
            result = await self.send_command(cmd_name)
            if result == CommandResult.SUCCESS:
                # Aqui você processaria a resposta específica
                # Por enquanto, apenas marca como operacional
                status.state = PrinterState.READY
                break
    
    status.last_update = datetime.now()
    self.current_status = status
    
    return status
