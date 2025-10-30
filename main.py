#!/usr/bin/env python3
"""Pipeline automático de impressão K1 Max"""

import yaml
import time
import logging
import sys
from pathlib import Path

from src.adapters.metaverso_client import MetaversoAPIClient
from src.adapters.converter import convert_glb_to_stl
from src.adapters.creality_driver import CrealityDriver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Carrega configuração"""
    config_path = Path(__file__).parent / 'config' / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def process_job(job, config, api, driver):
    """Processa um job de impressão"""
    try:
        # Salvar GLB usando método da API
        models_dir = Path(config['paths']['project_root']) / config['paths']['models']
        models_dir.mkdir(exist_ok=True)
        
        glb_path = api.save_object_file(
            job.get('file_data'), 
            job['object_id'], 
            output_dir=str(models_dir)
        )
        
        if not glb_path:
            logger.error("Falha ao salvar GLB")
            return False
        
        # Converter para STL
        stl_path = convert_glb_to_stl(glb_path)
        if not stl_path:
            return False
        
        # Iniciar slicer
        if not driver.start_slicer():
            return False
        
        # Pipeline GUI
        if not driver.import_stl(stl_path):
            driver.cleanup()
            return False
        
        if not driver.apply_preset():
            driver.cleanup()
            return False
        
        if not driver.slice_model():
            driver.cleanup()
            return False
        
        if not driver.send_to_printer():
            driver.cleanup()
            return False
        
        driver.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"Erro ao processar job: {e}")
        driver.cleanup()
        return False

def main():
    """Loop principal"""
    logger.info("Sistema iniciado - K1 Max")
    
    logger.info("Carregando configuração...")
    config = load_config()
    logger.info("✓ Configuração carregada")
    
    logger.info("Inicializando API client...")
    api = MetaversoAPIClient()
    logger.info("✓ API client inicializado")
    
    logger.info("Inicializando driver impressora...")
    driver = CrealityDriver(config)
    logger.info("✓ Driver inicializado")
    
    # Autenticar
    logger.info("Tentando autenticar...")
    try:
        if not api.authenticate():
            logger.error("Falha na autenticação")
            sys.exit(1)
        logger.info("✓ Autenticado com sucesso")
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        sys.exit(1)
    
    logger.info("Iniciando loop de monitoramento...")
    
    try:
        while True:
            logger.info("Consultando fila de impressão...")
            
            # Buscar jobs da fila
            try:
                jobs = api.get_printable_objects(include_file=True)
                logger.info(f"✓ Fila consultada: {len(jobs) if jobs else 0} jobs")
            except Exception as e:
                logger.error(f"Erro ao consultar fila: {e}")
                time.sleep(config['polling']['interval'])
                continue
            
            if jobs and len(jobs) > 0:
                job = jobs[0]
                job_id = job.get('object_id')
                
                if not job_id:
                    logger.error("Job sem object_id")
                    time.sleep(config['polling']['interval'])
                    continue
                
                logger.info(f"Processando job {job_id}")
                
                if process_job(job, config, api, driver):
                    api.mark_object_printing(job_id)
                    logger.info(f"✓ Job {job_id} concluído")
                else:
                    logger.error(f"✗ Job {job_id} falhou")
            else:
                logger.info("Fila vazia - aguardando...")
            
            logger.info(f"Aguardando {config['polling']['interval']}s...")
            time.sleep(config['polling']['interval'])
            
    except KeyboardInterrupt:
        logger.info("Shutdown solicitado")
        driver.cleanup()
        sys.exit(0)

if __name__ == "__main__":
    main()