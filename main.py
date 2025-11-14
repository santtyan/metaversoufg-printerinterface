#!/usr/bin/env python3
"""
Pipeline Principal: Metaverso UFG → Impressão 3D
Arquitetura conforme especificação do coordenador
"""

import sys
import time
import yaml
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Imports dos módulos criados
from api.metaverso_api import createMetaversoAPI
from utils.preset_utils import choosePreset
from utils.converter_utils import convertGlbtoSTL
from slicer.slicer_wrapper import sliceSTL

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def showHelp():
    """Exibe mensagem de ajuda"""
    print("Programa de Impressão 3D Automatizada - Metaverso UFG")
    print("Syntax: python main.py [help|--help|-h|CONFIGFILENAME]")
    print("\nO parâmetro é opcional. As três primeiras opções mostram esta mensagem.")
    print("A última opção é o nome do arquivo de configuração a ser aberto.")
    print("Se nenhum parâmetro for informado, o arquivo padrão 'config.yaml' será utilizado.\n")

def loadConfig(configFilename):
    """Carrega configuração do arquivo YAML"""
    try:
        with open(configFilename, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        logger.info(f"✓ Configuração carregada: {configFilename}")
        return cfg
    except FileNotFoundError:
        logger.error(f"✗ Arquivo de configuração não encontrado: {configFilename}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Erro ao carregar configuração: {e}")
        sys.exit(1)

def download_glb(obj_glb, cfg):
    """
    Baixa arquivo GLB do servidor
    
    Args:
        obj_glb: Objeto com dados do GLB
        cfg: Configuração
    
    Returns:
        Caminho do GLB baixado ou None
    """
    import base64
    
    # Se tem dados base64, salvar diretamente
    if obj_glb.get('glb_data'):
        try:
            glb_data = base64.b64decode(obj_glb['glb_data'])
            glb_path = Path(cfg['paths']['models']) / f"{obj_glb['object_id']}.glb"
            glb_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(glb_path, 'wb') as f:
                f.write(glb_data)
            
            logger.info(f"✓ GLB salvo: {glb_path.name}")
            return str(glb_path)
        except Exception as e:
            logger.error(f"✗ Erro ao salvar GLB: {e}")
            return None
    
    # Caso contrário, tentar download via URL
    # TODO: Implementar quando MinIO estiver totalmente configurado
    logger.warning("⚠ Download via URL não implementado ainda")
    return None

def print_gcode(gcode_path, cfg):
    """
    Envia G-code para impressão (stub)
    
    Args:
        gcode_path: Caminho do arquivo G-code
        cfg: Configuração
    
    Returns:
        True se enviado com sucesso
    """
    import subprocess
    
    # Abrir G-code no Creality Print (associação Windows)
    try:
        subprocess.Popen([str(Path(gcode_path).absolute())], shell=True)
        logger.info(f"✓ G-code aberto no Creality Print: {Path(gcode_path).name}")
        logger.info("⚠ ATENÇÃO: Clique manualmente em 'Enviar' no Creality Print")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao abrir G-code: {e}")
        return False

def main():
    """Função principal - loop de processamento"""
    
    # Processar argumentos de linha de comando
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["help", "--help", "-h"]:
            showHelp()
            return 0
        else:
            configFilename = arg
    else:
        configFilename = "config/config.yaml"
    
    print(f"Arquivo de configuração: '{configFilename}'")
    
    # Carregar configuração
    cfg = loadConfig(configFilename)
    
    # Inicializar API
    logger.info("Inicializando Metaverso API...")
    api = createMetaversoAPI(cfg)
    
    # Loop principal de processamento
    logger.info("="*60)
    logger.info("SISTEMA INICIADO - Aguardando objetos na fila")
    logger.info("="*60)
    
    try:
        while True:
            # Buscar objeto do servidor
            obj_glb = api.getObjectFromServer()
            
            if obj_glb is not None:
                logger.info("="*60)
                logger.info(f"NOVO OBJETO: {obj_glb['object_name']}")
                logger.info("="*60)
                
                try:
                    # 1. Baixar GLB
                    logger.info("[1/5] Baixando GLB...")
                    glb_path = download_glb(obj_glb, cfg)
                    
                    if not glb_path:
                        logger.error("✗ Falha no download - pulando objeto")
                        continue
                    
                    # Adicionar caminho ao objeto para próximas funções
                    obj_glb['glb_path'] = glb_path
                    
                    # 2. Escolher preset
                    logger.info("[2/5] Selecionando preset...")
                    preset = choosePreset(cfg, obj_glb)
                    
                    # 3. Converter GLB para STL
                    logger.info("[3/5] Convertendo GLB → STL...")
                    obj_stl = convertGlbtoSTL(cfg, obj_glb, preset)
                    
                    if not obj_stl:
                        logger.error("✗ Conversão GLB→STL falhou")
                        continue
                    
                    # 4. Fatiar STL para G-code
                    logger.info("[4/5] Fatiando STL → G-code...")
                    obj_gcode = sliceSTL(cfg, obj_stl, preset)
                    
                    if not obj_gcode:
                        logger.error("✗ Slicing falhou")
                        continue
                    
                    # 5. Enviar para impressão
                    logger.info("[5/5] Enviando para impressão...")
                    success = print_gcode(obj_gcode, cfg)
                    
                    if success:
                        # Informar backend que objeto foi enviado
                        api.informPrinting(obj_glb['object_id'])
                        logger.info("="*60)
                        logger.info("✅ PIPELINE CONCLUÍDO COM SUCESSO")
                        logger.info("="*60)
                    else:
                        logger.error("✗ Falha ao enviar para impressão")
                
                except Exception as e:
                    logger.error(f"✗ Erro no processamento: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Aguardar próximo ciclo
            waittime = cfg['metaverso'].get('waittime', 30)
            logger.info(f"Aguardando {waittime}s até próxima verificação...")
            time.sleep(waittime)
    
    except KeyboardInterrupt:
        logger.info("\n⚠ Sistema interrompido pelo usuário")
        return 0
    except Exception as e:
        logger.error(f"✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
