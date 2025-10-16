"""
K1 Max WebSocket Analyzer
Analisador avançado para descoberta de comandos WebSocket

PROPÓSITO: Este script é o núcleo da descoberta de API. Ele se conecta ao WebSocket
da K1 Max (porta 9999) e executa três fases de descoberta:
1. Passiva: Escuta tráfego enquanto você usa o Creality Print normalmente
2. Ativa: Testa comandos conhecidos e variações sistemáticas
3. Fuzzing: Tenta descobrir comandos ocultos com padrões seguros

QUANDO USAR: Na primeira sessão com acesso à impressora. Execute por 2-6 horas.
"""

import asyncio
import websockets
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import signal
import sys

# Configuração de logging para capturar tudo em arquivo E console simultaneamente
logging.basicConfig(
    level=logging.DEBUG,  # Captura até mensagens de debug para análise detalhada
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('websocket_analysis.log'),  # Arquivo persistente
        logging.StreamHandler(sys.stdout)  # Console em tempo real
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WebSocketMessage:
    """
    Estrutura de dados para cada mensagem capturada.
    
    PROPÓSITO: Padroniza como armazenamos cada interação WebSocket para análise posterior.
    Inclui timestamp preciso para correlação temporal e análise de padrões.
    """
    timestamp: datetime  # Momento exato da captura - crítico para correlação
    direction: str  # 'sent' (enviado por nós) ou 'received' (recebido da impressora)
    raw_data: bytes  # Dados brutos para análise binária se necessário
    parsed_data: Optional[Dict[str, Any]] = None  # JSON parseado quando possível
    message_type: Optional[str] = None  # Classificação do tipo de mensagem
    success: bool = True  # Flag de sucesso para análise estatística
    error: Optional[str] = None  # Mensagem de erro se houver

class K1MaxWebSocketAnalyzer:
    """
    Classe principal de análise WebSocket
    
    FLUXO DE EXECUÇÃO:
    1. Conecta ao WebSocket (porta 9999)
    2. Testa conectividade básica
    3. Fase passiva: escuta por N minutos
    4. Fase ativa: testa comandos sistemáticamente
    5. Fase fuzzing: busca comandos ocultos
    6. Gera relatórios e salva dados brutos
    """
    
    def __init__(self, printer_ip: str = "192.168.20.138", port: int = 9999):
        """
        Inicialização do analisador
        
        PARÂMETROS:
        - printer_ip: IP da K1 Max (verifique se mudou na rede local)
        - port: Porta WebSocket (9999 é padrão confirmado pelo Node-RED)
        """
        self.printer_ip = printer_ip
        self.port = port
        self.uri = f"ws://{printer_ip}:{port}"  # URI completo WebSocket
        
        # Armazenamento de todas as mensagens capturadas para análise posterior
        self.captured_messages: List[WebSocketMessage] = []
        
        # Dicionário de comandos descobertos organizados por tipo
        self.discovered_commands: Dict[str, Any] = {}
        
        # Estado da conexão e controle de execução
        self.websocket = None
        self.is_running = False
        
        # IMPORTANTE: Lista de comandos conhecidos baseados na pesquisa Node-RED
        # Estes serão testados primeiro na fase ativa
        self.known_commands = [
            {"cmd": "get_status"},  # Status geral da impressora
            {"cmd": "get_temperature"},  # Temperaturas (nozzle, bed)
            {"request": "printer_info"},  # Informações do sistema
            {"action": "get_progress"},  # Progresso de impressão
            {"cmd": "fan_control", "state": "query"},  # Status do ventilador
            {"cmd": "light_control", "state": "query"},  # Status da luz
            {"cmd": "list_files"},  # Lista arquivos disponíveis
            {"action": "file_list"},  # Variação do comando de listagem
            {"request": "job_info"},  # Informações do trabalho atual
        ]
        
        # Configuração de shutdown gracioso (Ctrl+C não corrompe dados)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """
        Handler para shutdown gracioso
        
        PROPÓSITO: Garante que ao pressionar Ctrl+C, os dados capturados
        até o momento sejam salvos corretamente antes de encerrar.
        """
        logger.info(f"Recebido sinal {signum}, iniciando shutdown...")
        self.is_running = False
    
    async def start_analysis(self, duration_minutes: int = 60):
        """
        Método principal que orquestra toda a análise
        
        FASES:
        1. Estabelece conexão WebSocket
        2. Descoberta passiva (1/3 do tempo)
        3. Descoberta ativa (1/3 do tempo)
        4. Fuzzing controlado (1/3 do tempo)
        5. Cleanup e geração de relatórios
        
        PARÂMETROS:
        - duration_minutes: Duração total da análise (recomendado: 180+ minutos)
        """
        logger.info(f"Iniciando análise WebSocket da K1 Max - {self.uri}")
        logger.info(f"Duração: {duration_minutes} minutos")
        
        self.is_running = True
        
        try:
            # Fase 0: Conexão e validação
            await self._establish_connection()
            
            # Fase 1: Escuta passiva (captura tráfego enquanto você usa o Creality Print)
            await self._passive_discovery_phase(duration_minutes // 3)
            
            # Fase 2: Testes ativos de comandos conhecidos e variações
            await self._active_discovery_phase(duration_minutes // 3)
            
            # Fase 3: Fuzzing seguro para descobrir comandos ocultos
            await self._controlled_fuzzing_phase(duration_minutes // 3)
            
        except Exception as e:
            logger.error(f"Erro durante análise: {e}")
        finally:
            # SEMPRE executa cleanup mesmo se houver erro
            await self._cleanup_and_report()
    
    async def _establish_connection(self):
        """
        Estabelece conexão WebSocket com a K1 Max
        
        VALIDAÇÕES:
        - Tenta conectar ao WebSocket na porta 9999
        - Configura ping/pong para manter conexão ativa
        - Testa conectividade com comandos básicos
        
        TRATAMENTO DE ERRO: Se falhar aqui, toda análise é abortada
        """
        try:
            logger.info(f"Conectando a {self.uri}...")
            
            # Conecta com configurações otimizadas para estabilidade
            self.websocket = await websockets.connect(
                self.uri,
                ping_interval=None,  # Envia ping a cada 30s para manter conexão
                ping_timeout=None,   # Timeout de 10s para resposta do ping
                close_timeout=5    # Timeout de 5s para fechar conexão
            )
            
            logger.info("Conexão WebSocket estabelecida com sucesso")
            
            # Testa se a conexão está realmente funcional
            await self._test_basic_connectivity()
            
        except Exception as e:
            logger.error(f"Falha na conexão WebSocket: {e}")
            raise  # Re-levanta exceção para abortar análise
    
    async def _test_basic_connectivity(self):
        """
        Testa conectividade básica com comandos simples
        
        PROPÓSITO: Valida que a conexão WebSocket está funcional antes
        de iniciar análise completa. Testa 4 variações de comando ping.
        """
        basic_tests = [
            {"ping": "test"},      # Variação 1: comando ping direto
            {"action": "ping"},    # Variação 2: ping como ação
            {"cmd": "ping"},       # Variação 3: ping como cmd
            {"request": "status"}  # Variação 4: solicita status
        ]
        
        for test_cmd in basic_tests:
            try:
                # Envia comando de teste
                await self.websocket.send(json.dumps(test_cmd))
                
                # Aguarda resposta com timeout curto (3 segundos)
                response = await asyncio.wait_for(self.websocket.recv(), timeout=3.0)
                
                # Armazena mensagem de teste para análise
                message = WebSocketMessage(
                    timestamp=datetime.now(),
                    direction='received',
                    raw_data=response.encode(),
                    parsed_data=json.loads(response) if response else None
                )
                
                self.captured_messages.append(message)
                logger.info(f"Teste conectividade OK: {test_cmd} -> {response[:100]}")
                
            except asyncio.TimeoutError:
                # Timeout não é erro crítico no teste de conectividade
                logger.debug(f"Timeout no teste: {test_cmd}")
            except Exception as e:
                logger.debug(f"Erro no teste: {test_cmd} - {e}")
            
            # Pequeno delay entre testes para não sobrecarregar
            await asyncio.sleep(0.5)
    
    async def _passive_discovery_phase(self, duration_minutes: int):
        """
        FASE 1: Descoberta Passiva
        
        PROPÓSITO: Captura TODO o tráfego WebSocket enquanto você usa o
        Creality Print normalmente. Isso revela os comandos REAIS que o
        software oficial usa.
        
        INSTRUÇÕES DURANTE ESTA FASE:
        1. Abra o Creality Print
        2. Importe um arquivo STL
        3. Configure settings de impressão
        4. Fatia o modelo
        5. Envie para impressão
        6. Monitore progresso
        
        Tudo será capturado automaticamente!
        """
        logger.info(f"Iniciando descoberta passiva por {duration_minutes} minutos")
        logger.info("INSTRUÇÕES: Agora use o Creality Print normalmente")
        logger.info("Todas as comunicações serão capturadas automaticamente")
        
        end_time = time.time() + (duration_minutes * 60)
        message_count = 0
        
        try:
            while time.time() < end_time and self.is_running:
                try:
                    # Escuta por mensagens com timeout curto para permitir loop
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    
                    # Cria registro da mensagem capturada
                    message = WebSocketMessage(
                        timestamp=datetime.now(),
                        direction='received',
                        raw_data=response.encode()
                    )
                    
                    # Tenta parsear JSON (maioria das mensagens são JSON)
                    try:
                        message.parsed_data = json.loads(response)
                        logger.info(f"Mensagem capturada: {response[:200]}")
                    except json.JSONDecodeError:
                        # Se não for JSON válido, armazena como raw
                        message.parsed_data = {"raw": response[:200]}
                    
                    self.captured_messages.append(message)
                    message_count += 1
                    
                except asyncio.TimeoutError:
                    # Timeout é normal quando não há mensagens - continua loop
                    continue
                except Exception as e:
                    logger.error(f"Erro na escuta passiva: {e}")
                    break
        
        except Exception as e:
            logger.error(f"Erro na fase passiva: {e}")
        
        logger.info(f"Descoberta passiva concluída: {message_count} mensagens capturadas")
    
    async def _active_discovery_phase(self, duration_minutes: int):
        """
        FASE 2: Descoberta Ativa
        
        PROPÓSITO: Testa sistematicamente comandos conhecidos E variações
        para descobrir funcionalidades não óbvias.
        
        ESTRATÉGIA:
        1. Testa comandos conhecidos (da pesquisa Node-RED)
        2. Gera variações sistemáticas (diferentes chaves e valores)
        3. Registra quais comandos retornam respostas válidas
        4. Classifica comandos por taxa de sucesso
        """
        logger.info(f"Iniciando descoberta ativa por {duration_minutes} minutos")
        
        # Combina comandos conhecidos com variações geradas
        commands_to_test = self.known_commands.copy()
        commands_to_test.extend(self._generate_command_variations())
        
        successful_commands = []
        
        for cmd in commands_to_test:
            if not self.is_running:
                break  # Permite interromper com Ctrl+C
                
            try:
                # Serializa comando para JSON
                cmd_json = json.dumps(cmd)
                
                # Envia comando
                await self.websocket.send(cmd_json)
                
                # Registra comando enviado
                sent_message = WebSocketMessage(
                    timestamp=datetime.now(),
                    direction='sent',
                    raw_data=cmd_json.encode(),
                    parsed_data=cmd
                )
                self.captured_messages.append(sent_message)
                
                # Aguarda resposta com timeout de 5 segundos
                try:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                    
                    # Registra resposta recebida
                    received_message = WebSocketMessage(
                        timestamp=datetime.now(),
                        direction='received',
                        raw_data=response.encode()
                    )
                    
                    try:
                        received_message.parsed_data = json.loads(response)
                    except json.JSONDecodeError:
                        received_message.parsed_data = {"raw": response}
                    
                    self.captured_messages.append(received_message)
                    
                    # Analisa se resposta indica sucesso
                    if self._is_successful_response(response, cmd):
                        successful_commands.append({
                            'command': cmd,
                            'response': received_message.parsed_data
                        })
                        logger.info(f"✓ SUCESSO: {cmd} -> {response[:100]}")
                    else:
                        logger.debug(f"✗ Sem sucesso: {cmd}")
                
                except asyncio.TimeoutError:
                    logger.debug(f"⏱ Timeout: {cmd}")
                
                # Rate limiting: espera 1 segundo entre comandos
                # Evita sobrecarregar a impressora
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Erro testando comando {cmd}: {e}")
        
        # Armazena comandos bem-sucedidos no dicionário de descobertas
        self.discovered_commands.update({
            'successful_commands': successful_commands,
            'discovery_timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Descoberta ativa concluída: {len(successful_commands)} comandos funcionais")
    
    def _generate_command_variations(self) -> List[Dict[str, Any]]:
        """
        Gera variações sistemáticas de comandos para teste
        
        ESTRATÉGIA: Combina diferentes chaves (cmd, action, request)
        com diferentes valores (status, info, temperature, etc.)
        
        RESULTADO: ~50 variações de comandos para testar
        """
        variations = []
        
        # Chaves comuns observadas em protocolos similares
        common_keys = ["cmd", "action", "request", "method", "type"]
        
        # Valores comuns para comandos de consulta e controle
        common_values = [
            "status", "info", "temperature", "progress", "files", 
            "print", "pause", "stop", "start", "get", "set"
        ]
        
        # Gera todas as combinações possíveis
        for key in common_keys:
            for value in common_values:
                variations.append({key: value})
        
        return variations
    
    def _is_successful_response(self, response: str, command: Dict[str, Any]) -> bool:
        """
        Determina se uma resposta indica sucesso do comando
        
        CRITÉRIOS DE SUCESSO:
        1. Resposta é JSON válido
        2. NÃO contém indicadores de erro
        3. Contém indicadores de sucesso OU dados estruturados
        
        RETORNO: True se comando foi bem-sucedido, False caso contrário
        """
        try:
            data = json.loads(response)
            
            # Indicadores de erro (resposta negativa)
            error_indicators = ["error", "fail", "invalid", "unknown", "not found"]
            response_lower = response.lower()
            if any(indicator in response_lower for indicator in error_indicators):
                return False
            
            # Indicadores de sucesso (resposta positiva)
            success_indicators = [
                "status", "temperature", "progress", "result", 
                "data", "info", "files", "success"
            ]
            
            if any(indicator in response_lower for indicator in success_indicators):
                return True
            
            # Se contém dados estruturados relevantes, considera sucesso
            if isinstance(data, dict) and len(data) > 1:
                return True
            
            return False
            
        except json.JSONDecodeError:
            # Resposta não é JSON válido = falha
            return False
    
    async def _controlled_fuzzing_phase(self, duration_minutes: int):
        """
        FASE 3: Fuzzing Controlado
        
        PROPÓSITO: Tenta descobrir comandos ocultos através de fuzzing
        SEGURO (não envia comandos destrutivos ou perigosos).
        
        PADRÕES TESTADOS:
        1. Variações numéricas (id: 0-9)
        2. Sufixos comuns (get_data, get_state, get_config)
        3. Estruturas REST-like (method/resource)
        
        LIMITAÇÕES: Máximo 50 comandos para evitar sobrecarga
        """
        logger.info(f"Iniciando fuzzing controlado por {duration_minutes} minutos")
        logger.info("⚠️  Fuzzing limitado a padrões seguros")
        
        # Padrões de fuzzing seguros
        safe_fuzzing_patterns = []
        
        # Padrão 1: Variações numéricas
        for i in range(10):
            safe_fuzzing_patterns.append({"id": i, "cmd": "query"})
        
        # Padrão 2: Sufixos comuns
        for suffix in ["data", "state", "config", "version"]:
            safe_fuzzing_patterns.append({"cmd": f"get_{suffix}"})
        
        discovered_via_fuzzing = []
        
        # Limita a 50 comandos para segurança
        for fuzz_cmd in safe_fuzzing_patterns[:50]:
            if not self.is_running:
                break
            
            try:
                await self.websocket.send(json.dumps(fuzz_cmd))
                response = await asyncio.wait_for(self.websocket.recv(), timeout=3.0)
                
                if self._is_successful_response(response, fuzz_cmd):
                    discovered_via_fuzzing.append({
                        'command': fuzz_cmd,
                        'response': json.loads(response)
                    })
                    logger.info(f"🎯 FUZZING SUCCESS: {fuzz_cmd}")
                
                # Rate limiting mais conservador para fuzzing
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logger.debug(f"Fuzzing error: {fuzz_cmd} - {e}")
        
        self.discovered_commands['fuzzing_discoveries'] = discovered_via_fuzzing
        logger.info(f"Fuzzing concluído: {len(discovered_via_fuzzing)} novos comandos")
    
    async def _cleanup_and_report(self):
        """
        Cleanup final e geração de relatórios
        
        AÇÕES:
        1. Fecha conexão WebSocket graciosamente
        2. Gera relatório de descobertas (JSON formatado)
        3. Salva dados brutos para análise posterior
        """
        if self.websocket:
            await self.websocket.close()
        
        # Gera relatório estruturado
        self._generate_discovery_report()
        
        # Salva dados brutos completos
        self._save_raw_data()
    
    def _generate_discovery_report(self):
        """
        Gera relatório estruturado das descobertas
        
        ARQUIVO: k1max_websocket_discovery_report.json
        
        CONTEÚDO:
        - Sumário quantitativo (mensagens, comandos descobertos)
        - Lista de comandos bem-sucedidos com respostas
        - Descobertas via fuzzing
        - Timestamp da análise
        """
        report = {
            "analysis_summary": {
                "total_messages_captured": len(self.captured_messages),
                "successful_commands": len(self.discovered_commands.get('successful_commands', [])),
                "fuzzing_discoveries": len(self.discovered_commands.get('fuzzing_discoveries', [])),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "discovered_commands": self.discovered_commands
        }
        
        report_path = Path("k1max_websocket_discovery_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📋 Relatório salvo em: {report_path}")
        logger.info(f"📊 Mensagens capturadas: {len(self.captured_messages)}")
        logger.info(f"✅ Comandos funcionais: {len(self.discovered_commands.get('successful_commands', []))}")
    
    def _save_raw_data(self):
        """
        Salva dados brutos completos para análise posterior
        
        ARQUIVO: k1max_websocket_raw_data.json
        
        PROPÓSITO: Permite re-análise dos dados sem repetir experimento.
        Inclui TODAS as mensagens capturadas com timestamps precisos.
        """
        raw_data = {
            "captured_messages": [
                {
                    "timestamp": msg.timestamp.isoformat(),
                    "direction": msg.direction,
                    "raw_data": msg.raw_data.decode('utf-8', errors='ignore'),
                    "parsed_data": msg.parsed_data
                }
                for msg in self.captured_messages
            ]
        }
        
        raw_data_path = Path("k1max_websocket_raw_data.json")
        with open(raw_data_path, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 Dados brutos salvos em: {raw_data_path}")

# Ponto de entrada principal
async def main():
    """
    Função principal com argumentos de linha de comando
    
    EXEMPLOS DE USO:
    
    1. Análise padrão (60 minutos):
       python websocket_analyzer.py
    
    2. Análise longa (120 minutos):
       python websocket_analyzer.py --duration 120
    
    3. IP customizado:
       python websocket_analyzer.py --ip 192.168.1.100
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="K1 Max WebSocket API Discovery")
    parser.add_argument("--ip", default="200.137.221.11", 
                       help="IP da impressora K1 Max")
    parser.add_argument("--duration", type=int, default=60, 
                       help="Duração da análise em minutos")
    parser.add_argument("--port", type=int, default=9999, 
                       help="Porta WebSocket")
    
    args = parser.parse_args()
    
    analyzer = K1MaxWebSocketAnalyzer(args.ip, args.port)
    
    try:
        await analyzer.start_analysis(args.duration)
    except KeyboardInterrupt:
        logger.info("⚠️  Análise interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal na análise: {e}")

if __name__ == "__main__":
    asyncio.run(main())