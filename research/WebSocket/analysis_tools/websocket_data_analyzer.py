"""
WebSocket Data Analysis Tool
Ferramenta para análise aprofundada dos dados capturados da K1 Max

PROPÓSITO: Processa os dados brutos gerados pelo websocket_analyzer.py e:
1. Identifica padrões de comandos
2. Classifica comandos por função
3. Mapeia comandos para respostas
4. Gera documentação da API descoberta
5. Cria cliente Python automaticamente

QUANDO USAR: Após executar websocket_analyzer.py. Pode ser executado em casa
com os arquivos JSON gerados no laboratório.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import re

class WebSocketDataAnalyzer:
    """
    Analisador avançado para dados capturados do WebSocket
    
    FLUXO DE ANÁLISE:
    1. Carrega dados brutos do arquivo JSON
    2. Separa comandos enviados de respostas recebidas
    3. Cria pares comando-resposta baseados em proximidade temporal
    4. Analisa padrões e estatísticas
    5. Gera documentação da API
    6. Cria cliente Python automatizado
    """
    
    def __init__(self, raw_data_file: str = "k1max_websocket_raw_data.json"):
        """
        Inicialização do analisador
        
        PARÂMETROS:
        - raw_data_file: Arquivo JSON gerado pelo websocket_analyzer.py
        
        IMPORTANTE: Execute este script no mesmo diretório onde está o arquivo
        k1max_websocket_raw_data.json gerado pela análise.
        """
        self.raw_data_file = Path(raw_data_file)
        
        # Estruturas de dados para análise
        self.messages = []  # Todas as mensagens
        self.commands = []  # Apenas comandos enviados
        self.responses = []  # Apenas respostas recebidas
        self.command_response_pairs = []  # Pares correlacionados
        
        # Carrega e processa dados
        self.load_data()
    
    def load_data(self):
        """
        Carrega e processa dados brutos capturados
        
        VALIDAÇÕES:
        - Verifica se arquivo existe
        - Valida estrutura JSON
        - Conta mensagens carregadas
        """
        if not self.raw_data_file.exists():
            raise FileNotFoundError(f"Arquivo de dados não encontrado: {self.raw_data_file}")
        
        with open(self.raw_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.messages = data.get('captured_messages', [])
        print(f"Carregado {len(self.messages)} mensagens para análise")
        
        # Separa comandos de respostas para análise individual
        self._separate_commands_and_responses()
    
    def _separate_commands_and_responses(self):
        """
        Separa mensagens em comandos enviados e respostas recebidas
        
        LÓGICA: Mensagens 'sent' são comandos que enviamos
               Mensagens 'received' são respostas da impressora
        
        Depois cria pares comando-resposta baseados em proximidade temporal
        """
        for msg in self.messages:
            if msg['direction'] == 'sent':
                self.commands.append(msg)
            elif msg['direction'] == 'received':
                self.responses.append(msg)
        
        # Cria pares comando-resposta
        self._create_command_response_pairs()
    
    def _create_command_response_pairs(self):
        """
        Cria pares comando-resposta baseados em timing
        
        ESTRATÉGIA: Para cada comando enviado, procura a resposta
        mais próxima temporalmente (dentro de 1 minuto).
        
        RESULTADO: Lista de dicionários com:
        - command: Comando enviado
        - response: Resposta recebida
        - delay_ms: Tempo de resposta em milissegundos
        """
        for i, cmd in enumerate(self.commands):
            cmd_time = datetime.fromisoformat(cmd['timestamp'])
            
            # Procura resposta mais próxima temporalmente
            best_response = None
            min_delay = timedelta(minutes=1)  # Máximo 1 minuto de delay
            
            for resp in self.responses:
                resp_time = datetime.fromisoformat(resp['timestamp'])
                delay = resp_time - cmd_time
                
                # Resposta deve ser DEPOIS do comando e dentro do threshold
                if timedelta(0) <= delay <= min_delay:
                    min_delay = delay
                    best_response = resp
            
            if best_response:
                self.command_response_pairs.append({
                    'command': cmd,
                    'response': best_response,
                    'delay_ms': min_delay.total_seconds() * 1000
                })
    
    def analyze_command_patterns(self) -> Dict[str, Any]:
        """
        Analisa padrões nos comandos descobertos
        
        ANÁLISES REALIZADAS:
        1. Estrutura dos comandos (quais chaves são usadas)
        2. Padrões de parâmetros (tipos de dados)
        3. Tipos de resposta (estruturas de retorno)
        4. Taxa de sucesso por comando
        
        RETORNO: Dicionário com todas as análises
        """
        print("Analisando padrões de comandos...")
        
        patterns = {
            'command_structures': defaultdict(int),  # Conta estruturas únicas
            'parameter_patterns': defaultdict(int),  # Conta padrões de parâmetros
            'response_types': defaultdict(int),      # Conta tipos de resposta
            'successful_commands': [],               # Lista de sucessos
            'failed_commands': []                    # Lista de falhas
        }
        
        for pair in self.command_response_pairs:
            cmd_data = pair['command'].get('parsed_data', {})
            resp_data = pair['response'].get('parsed_data', {})
            
            if isinstance(cmd_data, dict):
                # Analisa estrutura do comando (quais chaves contém)
                cmd_structure = tuple(sorted(cmd_data.keys()))
                patterns['command_structures'][cmd_structure] += 1
                
                # Analisa tipos de parâmetros
                for key, value in cmd_data.items():
                    param_pattern = f"{key}:{type(value).__name__}"
                    patterns['parameter_patterns'][param_pattern] += 1
                
                # Classifica como sucesso ou falha
                if self._is_successful_pair(pair):
                    patterns['successful_commands'].append(pair)
                else:
                    patterns['failed_commands'].append(pair)
            
            # Analisa tipos de resposta
            if isinstance(resp_data, dict):
                resp_structure = tuple(sorted(resp_data.keys()))
                patterns['response_types'][resp_structure] += 1
        
        return patterns
    
    def _is_successful_pair(self, pair: Dict[str, Any]) -> bool:
        """
        Determina se um par comando-resposta indica sucesso
        
        CRITÉRIOS:
        - Resposta contém 'result', 'data', ou 'status'
        - success: true na resposta
        - Não contém 'error'
        - Resposta tem conteúdo (não vazia)
        """
        resp_data = pair['response'].get('parsed_data', {})
        
        if isinstance(resp_data, dict):
            success_indicators = [
                'result' in resp_data,
                'data' in resp_data,
                'status' in resp_data,
                resp_data.get('success') is True,
                'error' not in resp_data,
                len(resp_data) > 1
            ]
            
            return any(success_indicators)
        
        return False
    
    def generate_api_documentation(self) -> Dict[str, Any]:
        """
        Gera documentação completa da API descoberta
        
        ESTRUTURA DA DOCUMENTAÇÃO:
        - metadata: Informações gerais da análise
        - endpoints: Cada comando descoberto documentado
        - command_reference: Referência rápida de comandos
        - response_schemas: Estruturas de resposta
        
        PROPÓSITO: Esta documentação pode ser usada para:
        1. Implementar cliente customizado
        2. Publicação científica
        3. Compartilhamento com comunidade
        """
        patterns = self.analyze_command_patterns()
        
        api_doc = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_commands_analyzed": len(self.command_response_pairs),
                "successful_commands": len(patterns['successful_commands']),
                "success_rate": len(patterns['successful_commands']) / len(self.command_response_pairs) if self.command_response_pairs else 0
            },
            "endpoints": {},
            "command_reference": {},
            "response_schemas": {}
        }
        
        # Documenta cada comando bem-sucedido
        for pair in patterns['successful_commands']:
            cmd_data = pair['command'].get('parsed_data', {})
            resp_data = pair['response'].get('parsed_data', {})
            
            if isinstance(cmd_data, dict):
                # Cria identificador único para o comando
                cmd_id = self._generate_command_id(cmd_data)
                
                api_doc['endpoints'][cmd_id] = {
                    'command_structure': cmd_data,
                    'response_example': resp_data,
                    'average_response_time_ms': pair['delay_ms'],
                    'success_rate': 1.0,
                    'description': self._generate_command_description(cmd_data, resp_data)
                }
        
        return api_doc
    
    def _generate_command_id(self, cmd_data: Dict[str, Any]) -> str:
        """
        Gera identificador único para um comando
        
        ESTRATÉGIA: Usa a chave principal do comando (cmd, action, request)
        e seu valor para criar um ID legível.
        
        EXEMPLOS:
        - {"cmd": "get_status"} -> "cmd_get_status"
        - {"action": "pause"} -> "action_pause"
        """
        if 'cmd' in cmd_data:
            return f"cmd_{cmd_data['cmd']}"
        elif 'action' in cmd_data:
            return f"action_{cmd_data['action']}"
        elif 'request' in cmd_data:
            return f"request_{cmd_data['request']}"
        else:
            # Fallback para estrutura genérica
            keys = sorted(cmd_data.keys())
            return f"generic_{'_'.join(keys[:2])}"
    
    def _generate_command_description(self, cmd_data: Dict[str, Any], resp_data: Dict[str, Any]) -> str:
        """
        Gera descrição automática do comando baseada nos dados
        
        ANÁLISE: Examina comando e resposta para inferir funcionalidade
        
        CATEGORIAS DETECTADAS:
        - Consulta/Status (get, status)
        - Controle/Configuração (set, control)
        - Operação/Execução (start, print)
        """
        descriptions = []
        
        # Analisa tipo de comando pelo conteúdo
        cmd_str = str(cmd_data).lower()
        if 'get' in cmd_str or 'status' in cmd_str:
            descriptions.append("Comando de consulta/status")
        elif 'set' in cmd_str or 'control' in cmd_str:
            descriptions.append("Comando de controle/configuração")
        elif 'start' in cmd_str or 'print' in cmd_str:
            descriptions.append("Comando de operação/execução")
        
        # Analisa resposta para inferir tipo de dados retornados
        if isinstance(resp_data, dict):
            resp_str = str(resp_data).lower()
            if 'temperature' in resp_str:
                descriptions.append("Retorna dados de temperatura")
            elif 'progress' in resp_str:
                descriptions.append("Retorna progresso de operação")
            elif 'status' in resp_str:
                descriptions.append("Retorna status do sistema")
        
        return " | ".join(descriptions) if descriptions else "Função não identificada"
    
    def create_command_reference_sheet(self):
        """
        Cria folha de referência dos comandos descobertos
        
        OUTPUTS:
        - k1max_api_reference.csv (planilha)
        - k1max_api_reference.html (visualização web)
        
        CONTEÚDO: Tabela com todos comandos descobertos, suas estruturas,
        tempos de resposta e taxas de sucesso.
        """
        api_doc = self.generate_api_documentation()
        
        # Cria DataFrame para análise em planilha
        commands_df = []
        for cmd_id, details in api_doc['endpoints'].items():
            commands_df.append({
                'Command ID': cmd_id,
                'Structure': str(details['command_structure']),
                'Response Time (ms)': details['average_response_time_ms'],
                'Description': details['description'],
                'Success Rate': details['success_rate']
            })
        
        df = pd.DataFrame(commands_df)
        
        # Salva em múltiplos formatos
        df.to_csv('k1max_api_reference.csv', index=False)
        df.to_html('k1max_api_reference.html', index=False)
        
        print(f"Referência de API criada: {len(df)} comandos documentados")
        return df
    
    def generate_python_client_template(self):
        """
        Gera template de cliente Python baseado nas descobertas
        
        OUTPUT: k1max_client_generated.py
        
        PROPÓSITO: Cria um cliente Python funcional com métodos para
        cada comando descoberto. Você pode usar este código diretamente
        em seu projeto.
        
        ESTRUTURA GERADA:
        - Classe K1MaxClient com conexão WebSocket
        - Método para cada comando descoberto
        - Documentação automática nos métodos
        - Exemplo de uso no final
        """
        api_doc = self.generate_api_documentation()
        
        # Início do código do cliente
        client_code = '''"""
K1 Max WebSocket Client
Gerado automaticamente baseado na análise de API
Data de geração: ''' + datetime.now().strftime('%d/%m/%Y %H:%M') + '''
"""

import asyncio
import websockets
import json
from typing import Dict, Any, Optional

class K1MaxClient:
    """Cliente WebSocket para K1 Max baseado em comandos descobertos"""
    
    def __init__(self, printer_ip: str = "200.137.221.11", port: int = 9999):
        """
        Inicializa cliente WebSocket
        
        Args:
            printer_ip: IP da impressora K1 Max
            port: Porta WebSocket (padrão: 9999)
        """
        self.uri = f"ws://{printer_ip}:{port}"
        self.websocket = None
    
    async def connect(self):
        """Conecta ao WebSocket da impressora"""
        self.websocket = await websockets.connect(self.uri)
        print(f"Conectado à K1 Max em {self.uri}")
    
    async def disconnect(self):
        """Desconecta do WebSocket"""
        if self.websocket:
            await self.websocket.close()
            print("Desconectado da K1 Max")
    
    async def send_command(self, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Envia comando e retorna resposta
        
        Args:
            command: Dicionário com comando a enviar
            
        Returns:
            Resposta da impressora ou None em caso de erro
        """
        try:
            await self.websocket.send(json.dumps(command))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            print(f"Erro enviando comando: {e}")
            return None

    # ===== MÉTODOS BASEADOS NOS COMANDOS DESCOBERTOS =====
'''
        
        # Adiciona métodos para cada comando descoberto
        for cmd_id, details in api_doc['endpoints'].items():
            method_name = cmd_id.replace('cmd_', '').replace('action_', '').replace('request_', '')
            cmd_struct = details['command_structure']
            
            # Gera método Python para o comando
            client_code += f'''
    async def {method_name}(self) -> Optional[Dict[str, Any]]:
        """
        {details['description']}
        
        Tempo de resposta típico: {details['average_response_time_ms']:.1f}ms
        Taxa de sucesso: {details['success_rate']:.1%}
        
        Returns:
            Resposta da impressora com dados do comando
        """
        command = {json.dumps(cmd_struct, indent=8)}
        return await self.send_command(command)
'''
        
        # Adiciona exemplo de uso
        client_code += '''

# ===== EXEMPLO DE USO =====
async def main():
    """Exemplo de como usar o cliente gerado"""
    
    # Cria e conecta cliente
    client = K1MaxClient()
    await client.connect()
    
    try:
        # Exemplo: obter status da impressora
        # (ajuste o nome do método conforme comandos descobertos)
        status = await client.get_status()
        print(f"Status da impressora: {status}")
        
        # Exemplo: obter temperatura
        temp = await client.get_temperature()
        print(f"Temperatura: {temp}")
        
    finally:
        # Sempre desconecta ao final
        await client.disconnect()

if __name__ == "__main__":
    # Executa exemplo
    asyncio.run(main())
'''
        
        # Salva cliente gerado
        with open('k1max_client_generated.py', 'w', encoding='utf-8') as f:
            f.write(client_code)
        
        print("Cliente Python gerado: k1max_client_generated.py")
        print("Você pode usar este código diretamente em seu projeto!")
    
    def generate_analysis_report(self):
        """
        Gera relatório completo da análise
        
        OUTPUT: k1max_analysis_complete_report.json
        
        CONTEÚDO COMPLETO:
        - Sumário executivo com estatísticas principais
        - Análise detalhada de padrões
        - Documentação completa da API
        - Recomendações de implementação
        
        PROPÓSITO: Este relatório é a base para:
        1. Publicação científica
        2. Documentação técnica
        3. Decisões de implementação
        """
        patterns = self.analyze_command_patterns()
        api_doc = self.generate_api_documentation()
        
        report = {
            'executive_summary': {
                'total_messages': len(self.messages),
                'command_response_pairs': len(self.command_response_pairs),
                'successful_commands': len(patterns['successful_commands']),
                'success_rate_percent': (len(patterns['successful_commands']) / len(self.command_response_pairs) * 100) if self.command_response_pairs else 0,
                'average_response_time_ms': sum(pair['delay_ms'] for pair in self.command_response_pairs) / len(self.command_response_pairs) if self.command_response_pairs else 0
            },
            'detailed_analysis': patterns,
            'api_documentation': api_doc,
            'recommendations': self._generate_implementation_recommendations(patterns, api_doc)
        }
        
        # Salva relatório
        with open('k1max_analysis_complete_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print("Relatório completo gerado: k1max_analysis_complete_report.json")
        return report
    
    def _generate_implementation_recommendations(self, patterns: Dict[str, Any], api_doc: Dict[str, Any]) -> List[str]:
        """
        Gera recomendações específicas de implementação
        
        ANÁLISE: Baseada na taxa de sucesso e quantidade de comandos,
        recomenda a melhor estratégia de implementação.
        
        CATEGORIAS DE RECOMENDAÇÃO:
        - Alta confiança (>80%): Substituir GUI completamente
        - Média confiança (50-80%): Abordagem híbrida
        - Baixa confiança (<50%): Manter GUI como principal
        """
        recommendations = []
        success_rate = api_doc['metadata']['success_rate']
        
        if success_rate > 0.8:
            recommendations.append("ALTA CONFIANÇA: WebSocket API é viável como substituto completo da GUI automation")
            recommendations.append("Implementar cliente nativo WebSocket como solução principal")
        elif success_rate > 0.5:
            recommendations.append("CONFIANÇA MODERADA: Implementar abordagem híbrida WebSocket + GUI fallback")
            recommendations.append("Priorizar comandos com maior taxa de sucesso para WebSocket")
        else:
            recommendations.append("BAIXA CONFIANÇA: Manter GUI automation como método principal")
            recommendations.append("Usar WebSocket apenas para monitoramento e comandos básicos")
        
        # Recomendações específicas baseadas na quantidade de comandos
        successful_cmds = len(patterns['successful_commands'])
        if successful_cmds > 10:
            recommendations.append(f"Foram descobertos {successful_cmds} comandos funcionais - API é rica o suficiente")
        
        recommendations.append("Implementar sistema de versionamento de protocolo para robustez")
        recommendations.append("Criar testes automatizados para validar comandos descobertos")
        
        return recommendations

def main():
    """
    Função principal para executar análise completa
    
    EXECUÇÃO:
    1. python websocket_data_analyzer.py
    
    OUTPUTS GERADOS:
    - k1max_api_reference.csv
    - k1max_api_reference.html
    - k1max_client_generated.py
    - k1max_analysis_complete_report.json
    """
    print("="*60)
    print("K1 Max WebSocket Data Analyzer")
    print("Iniciando análise completa dos dados capturados...")
    print("="*60)
    
    analyzer = WebSocketDataAnalyzer()
    
    # Executa análises
    patterns = analyzer.analyze_command_patterns()
    print(f"\nPadrões analisados: {len(patterns['successful_commands'])} comandos bem-sucedidos")
    
    # Gera documentação
    api_doc = analyzer.generate_api_documentation()
    print(f"API documentada: {len(api_doc['endpoints'])} endpoints descobertos")
    
    # Cria referência
    df = analyzer.create_command_reference_sheet()
    
    # Gera cliente
    analyzer.generate_python_client_template()
    
    # Relatório final
    report = analyzer.generate_analysis_report()
    
    print(f"\n{'='*60}")
    print("RESUMO EXECUTIVO")
    print(f"{'='*60}")
    print(f"Taxa de sucesso: {report['executive_summary']['success_rate_percent']:.1f}%")
    print(f"Tempo médio de resposta: {report['executive_summary']['average_response_time_ms']:.1f}ms")
    print(f"Comandos descobertos: {report['executive_summary']['successful_commands']}")
    
    print(f"\n{'='*60}")
    print("RECOMENDAÇÕES")
    print(f"{'='*60}")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\n{'='*60}")
    print("Análise completa! Arquivos gerados:")
    print("- k1max_api_reference.csv")
    print("- k1max_api_reference.html")
    print("- k1max_client_generated.py")
    print("- k1max_analysis_complete_report.json")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()