try:
    import requests
except ImportError:
    print("O módulo 'requests' não está instalado. Execute: pip install requests")
    exit(1)
try:
    import pyautogui
except ImportError:
    print("O módulo 'pyautogui' não está instalado. Execute: pip install pyautogui")
    exit(1)

import json
import base64
import subprocess
import time
import os 
import sys
import logging
import trimesh

# Configuração do logging para centralizada para rastreamento de eventos e erros
logging.basicConfig(
    level = logging.INFO,
    format= '%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

#---Função de Conversão de GLB para STL---
def convert_glb_to_stl(glb_filepath):
    try:
        logger.info(f"Iniciando conversão de GLB para STL: {os.path.basename(glb_filepath)}")

        if not os.path.exists(glb_filepath):
            logger.error(f"Erro: Arquivo GLB '{glb_filepath}' não encontrado.")
            return None
        
        stl_filepath = glb_filepath.replace('.glb', '.stl')
        mesh = trimesh.load(glb_filepath)
        mesh.export(stl_filepath)

        if os.path.exists(stl_filepath):
            logger.info(f"Conversão concluída: {os.path.basename(stl_filepath)}")
            return stl_filepath
        else:   
            logger.error(f"Erro: Falha ao criar o arquivo STL '{stl_filepath}'.")
            return None
    
    except Exception as e:
        logger.error(f"Erro na conversão de GLB para STL: {e}")
        return None   

# --- Configurações Essenciais ---
SLICER_PATH = r"C:\Program Files\Creality\Creality Print 6.2\CrealityPrint.exe"

# --- Pasta raiz do projeto (caminho dinâmico e portátil) ---
PROJECT_ROOT = r"C:\Projetos\metaversoufg-printerinterface"

# --- Pastas de recursos (referenciando a nova estrutura) ---
ASSETS_FOLDER = os.path.join(PROJECT_ROOT, 'assets')
MODELS_FOLDER = os.path.join(PROJECT_ROOT, 'models')

# ============ MODIFICAÇÃO PARA K1MAX CONTROLLER ============
# Aceitar arquivo via argumento de linha de comando
if len(sys.argv) > 1:
    LOCAL_FILE_PATH = sys.argv[1]
    USE_LOCAL_FILE = True
else:
    USE_LOCAL_FILE = True
    LOCAL_FILE_PATH = os.path.join(MODELS_FOLDER, "charmander(1).glb")
# ============================================================

if not USE_LOCAL_FILE:
    # 1. Autenticação na API 
    AUTH_URL = "https://mverso.space/v1/auth/login"
    AUTH_PAYLOAD = {
        "email": "scanner@example.com",
        "password": "scanner" 
    }
    HEADERS = {}

    try:
        logger.info("Tentando autenticar na API do Metaverso...")
        response = requests.post(AUTH_URL, json=AUTH_PAYLOAD)
        response.raise_for_status()
        token = response.json().get("access_token")
        HEADERS["Authorization"] = f"Bearer {token}"
        logger.info("Autenticação bem-sucedida! Token obtido.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro fatal de autenticação: {e}")
        logger.info("Mudando para o modo teste...")
        USE_LOCAL_FILE = True

# --- Caminho do Arquivo de Preset de Configuração ---
PRESET_FILE_PATH = os.path.join(ASSETS_FOLDER, "metaverso_PLA.creality_printer")

# --- Nomes das Imagens dos Botões 
ARQUIVO_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'open_file_initial_button.png') 
IMPORTAR_MENU_ITEM_FIRST_IMAGE = os.path.join(ASSETS_FOLDER, 'file_menu_item.png') 
IMPORTAR_STL_SPECIFIC_ITEM_IMAGE = os.path.join(ASSETS_FOLDER, 'browse_button.png') 
ARRANGE_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'arrange_button.png')
IMPORT_CONFIG_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'import_config_button.png')
IMPORTAR_MENU_ITEM_SECOND_IMAGE = os.path.join(ASSETS_FOLDER, 'file_menu_item2.png') 
SLICE_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'slice_button.png') 
PRINT_SEND_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'print_send_button.png')
CRIAR_COPIA_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'criar_copia_button.png')
CERTO_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'certo_button.png')

# --- Função Auxiliar para Encontrar e Clicar ---
def find_and_click(image_path, timeout=30, confidence=0.9):
    location = None
    timeout_start = time.time()
    logger.info(f"Procurando '{os.path.basename(image_path)}' na tela...") 
    while location is None and (time.time() - timeout_start) < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=False)
        except Exception as e:
            logger.error(f"Erro ao tentar ler ou procurar imagem '{os.path.basename(image_path)}': {e}") 
        time.sleep(0.5) 
    if location:
        logger.info(f"Elemento '{os.path.basename(image_path)}' encontrado em: {location}. Clicando...")
        center_x = location.left + location.width / 2
        center_y = location.top + location.height / 2
        pyautogui.click(center_x, center_y)
        return True
    else:
        logger.error(f"Erro: Elemento '{os.path.basename(image_path)}' não encontrado na tela após {timeout} segundos.")
        return False

# --- Loop Principal de Execução ---
def main_loop():
    object_id = None
    slicer_process = None
    
    try:
        file_path = None

        if USE_LOCAL_FILE:
            if os.path.exists(LOCAL_FILE_PATH):
                file_path = LOCAL_FILE_PATH
                logger.info(f"Usando arquivo local: {file_path}")

                if file_path.endswith('.glb'):
                    stl_path = convert_glb_to_stl(file_path)
                    if stl_path:
                        file_path = stl_path
            else:
                logger.error(f"Erro: Arquivo '{LOCAL_FILE_PATH}' não encontrado.")
                return False
        else:
            API_URL = "https://mverso.space/v1/printer/printable?with_file=true"
            logger.info("Verificando a fila de impressão da API...")
            response = requests.get(API_URL, headers=HEADERS)
            response.raise_for_status()
            printable_objects = response.json()

            if not printable_objects:
                logger.info("Nenhum objeto disponível para impressão.")
                return False

            object_to_print = printable_objects[0]
            object_id = object_to_print.get("object_id")
            file_content_base64 = object_to_print.get("object_file")
    
            file_path = os.path.join(MODELS_FOLDER, f"{object_id}.glb")
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(file_content_base64))
            logger.info(f"Arquivo '{os.path.basename(file_path)}' baixado.")

            if file_path.endswith('.glb'):  
                stl_path = convert_glb_to_stl(file_path)
                if stl_path:
                    file_path = stl_path

        if not file_path or not os.path.exists(file_path):
            logger.error(f"Erro fatal: Arquivo '{file_path}' não encontrado.")
            return False            
 
        # --- Automação de UI ---
        logger.info(f"Iniciando o slicer: {SLICER_PATH}")
        slicer_process = subprocess.Popen([SLICER_PATH], shell=True)
        time.sleep(25)
        logger.info("Iniciando a automação do fluxo STL -> Fatiamento -> Impressão...")

        # 1. Menu Arquivo
        if not find_and_click(ARQUIVO_BUTTON_IMAGE):
            logger.critical("Falha: Botão 'Arquivo' não encontrado.")
            sys.exit(1)
        time.sleep(1.5)

        # 2. Importar
        if not find_and_click(IMPORTAR_MENU_ITEM_FIRST_IMAGE):
            logger.critical("Falha: Item 'Importar' não encontrado.")
            sys.exit(1)
        time.sleep(1.5)

        # 3. Importar STL
        if not find_and_click(IMPORTAR_STL_SPECIFIC_ITEM_IMAGE):
            logger.critical("Falha: Item 'Importar STL' não encontrado.")
            sys.exit(1)
        time.sleep(2.5)

        # 4. Digitar caminho
        logger.info(f"Digitando o caminho: {file_path}")
        pyautogui.typewrite(file_path)
        pyautogui.press('enter')
        time.sleep(15)

        logger.info(f"Arquivo '{os.path.basename(file_path)}' carregado.")

        # --- Importar Configurações ---
        logger.info("Importando configurações...")
        if not find_and_click(ARQUIVO_BUTTON_IMAGE):
            sys.exit(1)
        time.sleep(1.5)
        if not find_and_click(IMPORTAR_MENU_ITEM_FIRST_IMAGE):
            sys.exit(1)
        time.sleep(1.5)
        if not find_and_click(IMPORTAR_MENU_ITEM_SECOND_IMAGE):
            sys.exit(1)
        time.sleep(1.5)
        if not find_and_click(IMPORT_CONFIG_BUTTON_IMAGE):
            sys.exit(1)
        time.sleep(2.5)
        
        logger.info(f"Digitando preset: {PRESET_FILE_PATH}")
        pyautogui.typewrite(PRESET_FILE_PATH)
        pyautogui.press('enter')
        time.sleep(5)

        # Resolver conflitos
        time.sleep(3)
        if find_and_click(CRIAR_COPIA_BUTTON_IMAGE, timeout=5, confidence=0.8):
            logger.info("Criou cópia para resolver conflito.")
        time.sleep(2)

        if not find_and_click(CERTO_BUTTON_IMAGE, timeout=5, confidence=0.8):
            pyautogui.press('enter')
            time.sleep(2)     

        logger.info("Configurações importadas.")
        
        # --- Arranjar ---
        if not find_and_click(ARRANGE_BUTTON_IMAGE):
            sys.exit(1)
        time.sleep(5)
        logger.info("Objetos organizados.")

        #Aguardar interface estabilizar antes de fatiar
        time.sleep(2)
        
        # --- Fatiar ---
        if find_and_click(SLICE_BUTTON_IMAGE, timeout=15, confidence=0.7):
            logger.info("Botão Fatiar encontrado.")
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
            logger.info("Fatiamento iniciado.")
            time.sleep(20)
        else: 
            logger.info("Botão Fatiar não encontrado, usando coordenadas fixas...")
            pyautogui.click(1244, 656)
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
            logger.info("Fatiamento iniciado (fallback).")
            time.sleep(20)

        logger.info("Fatiamento concluído.")

        # --Enviar Impressão---
        logger.info("Aguardando botão de envio...")
        time.sleep(3)

        # --- Enviar Impressão ---
        if find_and_click(PRINT_SEND_BUTTON_IMAGE, timeout=45, confidence=0.75):
            logger.info("Botão 'Imprimir/Enviar' encontrado.") 
            time.sleep(1)
            pyautogui.click()
            
            if not USE_LOCAL_FILE:
                patch_url = f"https://mverso.space/v1/printer/print/{object_id}"
                try:
                    response = requests.patch(patch_url, headers=HEADERS)
                    response.raise_for_status()
                    logger.info("Status atualizado na API.")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Erro ao atualizar API: {e}") 
            
            time.sleep(5)
            logger.info("Comando enviado para K1 Max!")
            logger.info("Automação concluída.")
        else:
            logger.error("Falha ao encontrar botão 'Imprimir/Enviar'.")
    except Exception as e:  
        logger.critical(f"Erro inesperado: {e}", exc_info=True)
        return False
    finally:
        if slicer_process is not None and slicer_process.poll() is None: 
            logger.info("Fechando o slicer...")
            slicer_process.terminate()
            time.sleep(5) 
            if slicer_process.poll() is None: 
                slicer_process.kill() 
            logger.info("Slicer fechado.")

if __name__ == "__main__":
    main_loop()