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
PROJECT_ROOT = r"C:\Users\USER\Documents\metaversoufg-printerinterface"

# --- Pastas de recursos (referenciando a nova estrutura) ---
ASSETS_FOLDER = os.path.join(PROJECT_ROOT, 'assets')
MODELS_FOLDER = os.path.join(PROJECT_ROOT, 'models')

#MODO TESTE - usar arquivo local válido em vez de API
USE_LOCAL_FILE = True # Defina como False quando quiser usar a API
LOCAL_FILE_PATH = os.path.join(MODELS_FOLDER, "charmander(1).glb") # Substitua pelo caminho do seu arquivo local

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
        response.raise_for_status() # Lança um erro para status de erro (4xx, 5xx)
        token = response.json().get("access_token")
        HEADERS["Authorization"] = f"Bearer {token}"
        logger.info("Autenticação bem-sucedida! Token obtido.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro fatal de autenticação: {e}")
        logger.info("Mudando para o modo teste...")
        USE_LOCAL_FILE = True

# --- Caminho do Arquivo de Preset de Configuração (Caminho corrigido) ---
PRESET_FILE_PATH = os.path.join(ASSETS_FOLDER, "metaverso_PLA.creality_printer")

# --- Nomes das Imagens dos Botões 
ARQUIVO_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'open_file_initial_button.png') 
IMPORTAR_MENU_ITEM_FIRST_IMAGE = os.path.join(ASSETS_FOLDER, 'file_menu_item.png') 
IMPORTAR_STL_SPECIFIC_ITEM_IMAGE = os.path.join(ASSETS_FOLDER, 'browse_button.png') 
ADDRESS_BAR_ICON_IMAGE = os.path.join(ASSETS_FOLDER, 'address_bar_icon.png') 
ARRANGE_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'arrange_button.png')
IMPORT_CONFIG_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'import_config_button.png')
IMPORTAR_MENU_ITEM_SECOND_IMAGE = os.path.join(ASSETS_FOLDER, 'file_menu_item2.png') 
SLICE_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'slice_button.png') 
PRINT_SEND_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'print_send_button.png')
CRIAR_COPIA_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'criar_copia_button.png')
CERTO_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'certo_button.png')


# --- Função Auxiliar para Encontrar e Clicar (Com Logging) ---
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
            # Usar arquivo local para teste
            if os.path.exists(LOCAL_FILE_PATH):
                file_path = LOCAL_FILE_PATH
                logger.info(f"Usando arquivo local para teste: {file_path}")

                #Conversão Simplificada usando a função
                if file_path.endswith('.glb'):
                    stl_path = convert_glb_to_stl(file_path)
                    if stl_path:
                        file_path = stl_path  # Usar STL na automação
            
            else:
                logger.error(f"Erro: O arquivo local '{LOCAL_FILE_PATH}' não é um GLB válido.")
                return False
        else:
            # 2. Obter a fila de impressão da API
            API_URL = "https://mverso.space/v1/printer/printable?with_file=true"
            logger.info("Verificando a fila de impressão da API...")
            response = requests.get(API_URL, headers=HEADERS)
            response.raise_for_status()
            printable_objects = response.json()

            if not printable_objects:
                logger.info("Nenhum objeto disponível para impressão. Aguardando...")
                time.sleep(30)
                return False

            # Use o primeiro objeto da fila
            object_to_print = printable_objects[0]
            object_id = object_to_print.get("object_id")
            file_content_base64 = object_to_print.get("object_file")
    
            # Decodificar o arquivo e salvá-lo localmente
            file_path = os.path.join(MODELS_FOLDER, f"{object_id}.glb")
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(file_content_base64))
            logger.info(f"Arquivo '{os.path.basename(file_path)}' baixado com sucesso.")# Converter GLB para STL

            #Conversão Simplificada usando a função
            if file_path.endswith('.glb'):  
                stl_path = convert_glb_to_stl(file_path)
                if stl_path:
                    file_path = stl_path  # Usar STL na automação
                else:
                    logger.info("Continuando com o arquivo GLB original.")
                    time.sleep(30)    

            #Converter GLB para STL se necessário
            if file_path.endswith('.glb'):
                logger.info("Convertendo GLB para STL...")
                try:
                    mesh = trimesh.load(file_path)
                    stl_path = file_path.replace('.glb', '.stl')
                    mesh.export(stl_path)
                    file_path = stl_path  # Usar STL na automação
                    logger.info(f"Conversão concluída: {os.path.basename(stl_path)}")
                except Exception as e:
                    logger.error(f"Erro na conversão: {e}")
                    logger.info("Continuando com o arquivo GLB original.")
                    time.sleep(30)    

        if not file_path or not os.path.exists(file_path):
            logger.error(f"Erro fatal: Arquivo '{file_path}' não encontrado após download.")
            return False            
 
        # --- Bloco de Automação de UI (Só é executado se houver objetos) ---
        logger.info(f"Iniciando o slicer: {SLICER_PATH}")
        slicer_process = subprocess.Popen([SLICER_PATH], shell=True)
        time.sleep(25) # Tempo para o slicer carregar completamente
        logger.info("Iniciando a automação do fluxo STL -> Fatiamento -> Impressão no slicer...")

        # --- INÍCIO DA LÓGICA DE AUTOMAÇÃO DE UI ---
        logger.info("Iniciando a automação para importar o arquivo...")

        # 1. Clica no menu 'Arquivo'
        if not find_and_click(ARQUIVO_BUTTON_IMAGE):
            logger.critical("Falha crítica: Botão 'Arquivo' não encontrado. Encerrando.")
            sys.exit(1)
        time.sleep(1.5)

        # 2. Clica no item de menu 'Importar'
        if not find_and_click(IMPORTAR_MENU_ITEM_FIRST_IMAGE):
            logger.critical("Falha crítica: Item de menu 'Importar' não encontrado. Encerrando.")
            sys.exit(1)
        time.sleep(1.5)

        # 3. Clica no item de menu 'Importar 3MF/STL/...'
        if not find_and_click(IMPORTAR_STL_SPECIFIC_ITEM_IMAGE):
            logger.critical("Falha crítica: Item 'Importar 3MF/STL/...' não encontrado. Encerrando.")
            sys.exit(1)
        time.sleep(2.5)

        # 4. Digita o caminho completo do arquivo baixado e pressiona Enter
        logger.info(f"Digitando o caminho do arquivo: {file_path}")
        pyautogui.typewrite(file_path)
        pyautogui.press('enter')
        time.sleep(15) # Tempo para o slicer carregar o modelo

        logger.info(f"Arquivo '{os.path.basename(file_path)}' carregado no slicer.")

        # --- INÍCIO DA SEÇÃO: IMPORTAR/SELECIONAR CONFIGURAÇÕES ---
        logger.info("\nIniciando a importação/seleção de configurações...")
        if not find_and_click(ARQUIVO_BUTTON_IMAGE):
            logger.error("Falha ao encontrar o botão/menu 'Arquivo' novamente.")
            sys.exit(1)
        time.sleep(1.5)
        if not find_and_click(IMPORTAR_MENU_ITEM_FIRST_IMAGE):
            logger.error("Falha ao encontrar o primeiro item de menu 'Importar' novamente.")
            sys.exit(1)
        time.sleep(1.5)
        if not find_and_click(IMPORTAR_MENU_ITEM_SECOND_IMAGE):
            logger.error("Falha ao encontrar o segundo item de menu 'Importar'.")
            sys.exit(1)
        time.sleep(1.5)
        if not find_and_click(IMPORT_CONFIG_BUTTON_IMAGE):
            logger.error("Falha ao encontrar o botão de Importar Configurações.")''
            sys.exit(1)
        time.sleep(2.5)
        logger.info(f"Digitando o caminho completo do arquivo de preset: {PRESET_FILE_PATH}")
        pyautogui.typewrite(PRESET_FILE_PATH)
        pyautogui.press('enter')
        time.sleep(5)
        logger.info("Configurações importadas/selecionadas (esperamos!).")

        #Lidar com janela de conflito de configuração, se aparecer
        time.sleep(3)

        CRIAR_COPIA_BUTTON_IMAGE = os.path.join(ASSETS_FOLDER, 'criar_copia_button.png')
        if find_and_click(CRIAR_COPIA_BUTTON_IMAGE, timeout=5, confidence=0.8):
            logger.info("Criou uma 'Criar uma Cópia' para resolver conflitos de configuração.")
        time.sleep(2)

        # Tentar clicar no botão "Certo" ou Enter como fallback
        if not find_and_click(CERTO_BUTTON_IMAGE, timeout=5, confidence=0.8):
            logger.info("Nenhum botão 'Certo' encontrado, tentando pressionar Enter como fallback.")
            pyautogui.press('enter')
            time.sleep(2)     

        # --- FIM DA SEÇÃO DE CONFIGURAÇÕES ---
        
        logger.info("\nObjetos carregados e configurações importadas.")
        
        # --- Clicar no botão "Arranjar" / "Organizar" Objetos na Mesa ---
        if not find_and_click(ARRANGE_BUTTON_IMAGE):
            logger.error("Falha ao encontrar o botão de 'Arranjar Objetos'.")
            sys.exit(1)
        time.sleep(5)
        logger.info("Objetos organizados na mesa.")
        
        # --- Clicar no botão "Fatiar" (Slice) ---
        if find_and_click(SLICE_BUTTON_IMAGE, timeout=5, confidence=0.6):
            logger.info("Fatiamento iniciado. Aguardando...")
            time.sleep(15) # Tempo para o fatiamento
        else: 
            #Segunda tentativa
            logger.info("Tentando clicar no botão 'Fatiar' novamente com parâmetros ajustados...")
            pyautogui.click(832, 635)
            time.sleep(2)
            logger.info("Fatiamento iniciado. Aguardando...")
            time.sleep(15) # Tempo para o fatiamento

        ## num_clicks_slice = 3
       ## for i in range(num_clicks_slice):
         ##   logger.info(f"Tentando clicar no botão Fatiar (tentativa {i+1}/{num_clicks_slice})...")
           ## if find_and_click(SLICE_BUTTON_IMAGE):
           ##     logger.info("Fatiamento iniciado. Aguardando...")
            ##    time.sleep(15)
            ##    break
           ## else:
            ##    logger.warning(f"Falha ao encontrar o botão 'Fatiar' na tentativa {i+1}.")
             ##   if i == num_clicks_slice - 1:
              ##      logger.critical("Falha persistente ao fatiar. Encerrando o script.")
               ##     sys.exit(1)
              ##  time.sleep(2)
        
        logger.info("Fatiamento concluído (esperamos!).")
    
        # --- FIM DA LÓGICA DE AUTOMAÇÃO DE UI ---
    
        # 4. Notifica a API que o objeto está sendo impresso 
        if find_and_click(PRINT_SEND_BUTTON_IMAGE):
            patch_url = f"https://mverso.space/v1/printer/print/{object_id}"
            try:
                response = requests.patch(patch_url, headers=HEADERS)
                response.raise_for_status()
                logger.info("Status de impressão atualizado na API.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao atualizar o status na API: {e}") 
            
            time.sleep(5)
            logger.info("Comando de impressão enviado para a K1 Max!")
            logger.info("\n--- Automação do fluxo completo  finalizada ---")
        else:
            logger.error(f"Falha ao encontrar o botão de 'Imprimir/Enviar',")
    except requests.exceptions.RequestException as e: 
        logger.error(f"Erro ao obter a fila de impressão: {e}")
        time.sleep(30)
        return False
    except Exception as e:  
        logger.critical(f"Ocorreu um erro inesperado durante a automação: {e}", exc_info=True)
        time.sleep(30)
        return False
    finally:
        if slicer_process is not None and slicer_process.poll() is None: 
            logger.info("\nFechando o slicer...")
            slicer_process.terminate()
            time.sleep(5) 
            if slicer_process.poll() is None: 
                slicer_process.kill() 
            logger.info("Slicer fechado.")
        else:
            logger.info("Slicer não foi iniciado ou já estava fechado.")
if __name__ == "__main__":
    main_loop()