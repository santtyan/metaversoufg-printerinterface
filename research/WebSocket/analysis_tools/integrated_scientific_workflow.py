"""
Integrated Scientific Workflow - Versão Simplificada
Orquestrador que integra análise WebSocket com logging científico

PROPÓSITO: Script OPCIONAL que automatiza todo o processo.
Para 3 horas de acesso, use os scripts individuais.

USO:
1. Workflow completo: python integrated_scientific_workflow.py --full --duration 120
2. Apenas análise: python integrated_scientific_workflow.py --analysis-only
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json

# Imports dos componentes
try:
    from websocket_analyzer import K1MaxWebSocketAnalyzer
    from websocket_data_analyzer import WebSocketDataAnalyzer
    from k1max_production_client import K1MaxProductionClient, CommandResult
except ImportError as e:
    print(f"ERRO: Componentes não encontrados: {e}")
    print("Certifique-se de que todos os scripts estão no mesmo diretório")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedWorkflow:
    """Orquestrador do workflow científico completo"""
    
    def __init__(self, experiment_name: str, printer_ip: str = "200.137.221.11"):
        self.experiment_name = experiment_name
        self.printer_ip = printer_ip
        self.results = {}
    
    async def run_discovery(self, duration_minutes: int) -> Dict[str, Any]:
        """Fase 1: Descoberta de comandos"""
        logger.info(f"=== FASE 1: DESCOBERTA ({duration_minutes} minutos) ===")
        
        analyzer = K1MaxWebSocketAnalyzer(self.printer_ip)
        await analyzer.start_analysis(duration_minutes)
        
        return {
            "messages_captured": len(analyzer.captured_messages),
            "commands_discovered": len(analyzer.discovered_commands.get('successful_commands', []))
        }
    
    async def run_analysis(self) -> Dict[str, Any]:
        """Fase 2: Análise de dados"""
        logger.info("=== FASE 2: ANÁLISE DE DADOS ===")
        
        analyzer = WebSocketDataAnalyzer()
        patterns = analyzer.analyze_command_patterns()
        api_doc = analyzer.generate_api_documentation()
        
        analyzer.create_command_reference_sheet()
        analyzer.generate_python_client_template()
        analyzer.generate_analysis_report()
        
        return {
            "successful_commands": len(patterns['successful_commands']),
            "success_rate": api_doc['metadata']['success_rate'] * 100
        }
    
    async def run_validation(self, runs: int = 10) -> Dict[str, Any]:
        """Fase 3: Validação experimental"""
        logger.info(f"=== FASE 3: VALIDAÇÃO ({runs} execuções) ===")
        
        client = K1MaxProductionClient(self.printer_ip)
        
        if not await client.connect():
            return {"status": "failed", "error": "connection_failed"}
        
        results = {"total": 0, "success": 0, "commands_tested": []}
        
        try:
            for cmd_name in list(client.discovered_commands.keys())[:5]:  # Testa primeiros 5
                logger.info(f"Validando: {cmd_name}")
                cmd_success = 0
                
                for _ in range(runs):
                    result = await client.send_command(cmd_name)
                    results["total"] += 1
                    if result == CommandResult.SUCCESS:
                        cmd_success += 1
                        results["success"] += 1
                    await asyncio.sleep(0.5)
                
                results["commands_tested"].append({
                    "command": cmd_name,
                    "success_rate": cmd_success / runs
                })
        finally:
            await client.disconnect()
        
        results["overall_success_rate"] = results["success"] / results["total"] if results["total"] > 0 else 0
        return results
    
    async def run_complete(self, discovery_minutes: int = 120, validation_runs: int = 10, skip_discovery: bool = False):
        """Executa workflow completo"""
        start_time = datetime.now()
        
        try:
            # Fase 1: Discovery
            if not skip_discovery:
                self.results['discovery'] = await self.run_discovery(discovery_minutes)
            
            # Fase 2: Analysis
            self.results['analysis'] = await self.run_analysis()
            
            # Fase 3: Validation
            self.results['validation'] = await self.run_validation(validation_runs)
            
            # Metadados
            self.results['metadata'] = {
                'experiment': self.experiment_name,
                'duration_minutes': (datetime.now() - start_time).total_seconds() / 60,
                'timestamp': datetime.now().isoformat()
            }
            
            # Salva resultados
            self.save_results()
            self.generate_readme()
            
            logger.info("=== WORKFLOW COMPLETO ===")
            logger.info(f"Comandos descobertos: {self.results.get('discovery', {}).get('commands_discovered', 'N/A')}")
            logger.info(f"Taxa de sucesso análise: {self.results.get('analysis', {}).get('success_rate', 0):.1f}%")
            logger.info(f"Taxa de sucesso validação: {self.results.get('validation', {}).get('overall_success_rate', 0):.1%}")
            
        except Exception as e:
            logger.error(f"Erro no workflow: {e}")
            self.results['error'] = str(e)
    
    def save_results(self):
        """Salva resultados em JSON"""
        output_file = f"{self.experiment_name}_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"Resultados salvos: {output_file}")
    
    def generate_readme(self):
        """Gera README com resumo"""
        readme = f"""# {self.experiment_name} - Resultados

## Resumo Executivo

**Descoberta:**
- Comandos descobertos: {self.results.get('discovery', {}).get('commands_discovered', 'N/A')}
- Mensagens capturadas: {self.results.get('discovery', {}).get('messages_captured', 'N/A')}

**Análise:**
- Comandos funcionais: {self.results.get('analysis', {}).get('successful_commands', 'N/A')}
- Taxa de sucesso: {self.results.get('analysis', {}).get('success_rate', 0):.1f}%

**Validação:**
- Execuções totais: {self.results.get('validation', {}).get('total', 'N/A')}
- Taxa de sucesso: {self.results.get('validation', {}).get('overall_success_rate', 0):.1%}

## Arquivos Gerados

- `k1max_websocket_raw_data.json` - Dados brutos
- `k1max_analysis_complete_report.json` - Análise completa
- `k1max_api_reference.csv` - Referência de comandos
- `k1max_client_generated.py` - Cliente Python

## Como Usar

```python
from k1max_production_client import K1MaxProductionClient

client = K1MaxProductionClient()
await client.connect()
result = await client.send_command('get_status')
await client.disconnect()
```

---
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        with open(f"{self.experiment_name}_README.md", "w", encoding='utf-8') as f:
            f.write(readme)

async def main():
    """Ponto de entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="K1 Max Integrated Workflow")
    parser.add_argument("--full", action="store_true", help="Workflow completo")
    parser.add_argument("--analysis-only", action="store_true", help="Apenas análise")
    parser.add_argument("--validation-only", action="store_true", help="Apenas validação")
    parser.add_argument("--duration", type=int, default=120, help="Duração descoberta (min)")
    parser.add_argument("--validation-runs", type=int, default=10, help="Execuções validação")
    parser.add_argument("--experiment-name", type=str, 
                       default=f"K1Max_{datetime.now().strftime('%Y%m%d_%H%M')}",
                       help="Nome do experimento")
    parser.add_argument("--ip", default="200.137.221.11", help="IP da impressora")
    
    args = parser.parse_args()
    
    workflow = IntegratedWorkflow(args.experiment_name, args.ip)
    
    try:
        if args.full:
            await workflow.run_complete(args.duration, args.validation_runs, skip_discovery=False)
        elif args.analysis_only:
            workflow.results['analysis'] = await workflow.run_analysis()
            workflow.save_results()
        elif args.validation_only:
            workflow.results['validation'] = await workflow.run_validation(args.validation_runs)
            workflow.save_results()
        else:
            print("Use: --full, --analysis-only, ou --validation-only")
            print("Exemplo: python integrated_scientific_workflow.py --full --duration 120")
    
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário")
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())