#!/usr/bin/env python3
"""
Pipeline Principal: Metaverso UFG → Impressão 3D
Entry point para automação completa
"""

import sys
import yaml
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_config(config_path="config/config.yaml"):
    """Carrega arquivo de configuração YAML"""
    with open(config_path) as f:
        return yaml.safe_load(f)


def main_mock_mode(cfg):
    """
    Modo MOCK: Processa GLBs locais sem depender da API
    Útil para testar pipeline quando MinIO está offline
    """
    from src.k1max.printer_pool import PrinterPool
    
    logger.info("="*60)
    logger.info("MODO MOCK: Processando GLBs locais")
    logger.info("="*60)
    
    # Inicializar pool de impressão
    pool = PrinterPool(cfg)
    pool.start()
    
    # Buscar GLBs na pasta models/
    models_dir = Path(cfg['paths']['project_root']) / cfg['paths']['models']
    glb_files = list(models_dir.glob("*.glb"))
    
    if not glb_files:
        logger.warning(f"⚠ Nenhum GLB encontrado em {models_dir}")
        logger.info("Adicione arquivos .glb em models/ para testar")
        return
    
    logger.info(f"✓ {len(glb_files)} GLBs detectados")
    
    # Processar cada GLB
    for glb_path in glb_files:
        logger.info(f"\n>>> Enfileirando: {glb_path.name}")
        pool.submit_job(glb_path)
        time.sleep(2)  # Simula intervalo entre jobs
    
    # Aguardar conclusão de todos os jobs
    logger.info("\n⏳ Aguardando conclusão de todos os jobs...")
    pool.queue.join()
    
    logger.info("\n" + "="*60)
    logger.info("✓ TODOS OS JOBS PROCESSADOS")
    logger.info("="*60)


def main_api_mode(cfg):
    """
    Modo API: Busca objetos do backend Metaverso
    Requer MinIO acessível
    """
    from src.k1max.printer_pool import PrinterPool
    from src.adapters.metaverso_client import MetaversoAPIClient
    
    logger.info("="*60)
    logger.info("MODO API: Conectando ao Metaverso")
    logger.info("="*60)
    
    # Inicializar componentes
    pool = PrinterPool(cfg)
    pool.start()
    
    api = MetaversoAPIClient()
    api.authenticate()
    logger.info("✓ Autenticado no backend")
    
    poll_interval = cfg['polling']['interval']
    logger.info(f"⏱ Intervalo de polling: {poll_interval}s")
    
    # Loop principal
    try:
        while True:
            logger.info("\n🔍 Consultando fila...")
            objs = api.get_printable_objects(include_file=True)
            
            if not objs:
                logger.info("Fila vazia")
            else:
                logger.info(f"✓ {len(objs)} objetos pendentes")
                
                for obj in objs:
                    obj_id = obj['object_id']
                    logger.info(f"\n>>> Processando {obj_id[:8]}...")
                    
                    # Download GLB
                    glb_path = api.save_object_file(
                        obj['object_file'], 
                        obj_id
                    )
                    
                    if glb_path:
                        # Enfileirar impressão
                        pool.submit_job(Path(glb_path))
                        
                        # Notificar backend
                        api.mark_object_printing(obj_id)
                        logger.info(f"✓ {obj_id[:8]} marcado como PRINTING")
                    else:
                        logger.error(f"⚠ Falha ao baixar {obj_id[:8]}")
            
            # Aguardar próximo ciclo
            time.sleep(poll_interval)
            
    except KeyboardInterrupt:
        logger.info("\n⏹ Interrompido pelo usuário")
        pool.queue.join()


def main():
    """Entry point principal"""
    cfg = load_config()
    
    # Verificar modo de operação via argumento
    if len(sys.argv) > 1 and sys.argv[1] == "--mock":
        main_mock_mode(cfg)
    else:
        # Tentar modo API, fallback para mock se falhar
        try:
            main_api_mode(cfg)
        except Exception as e:
            logger.error(f"⚠ Erro no modo API: {e}")
            logger.info("\n🔄 Tentando modo MOCK...")
            main_mock_mode(cfg)


if __name__ == "__main__":
    main()
