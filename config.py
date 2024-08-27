from botcity.maestro import BotMaestroSDK
import os

maestro = BotMaestroSDK()
maestro.login("https://oncoclinicas.botcity.dev", "oncoclinicas", "ONC_3Q7QALG3JJDHJCJCGLJL")

# Se ambiente_producao = True o robô usará todos os sistemas em ambiente de produção
AMBIENTE_PRODUCAO = False

# Se headless = True o robô não exibirá o navegador durante a execução
HEADLESS = False

# Dados do RPA
RPA_SHORT_NAME = 'RPA054'
RPA_FULL_NAME = 'RPA054_EXTRACAO_TRADIMUS_QUITACAO'
RPA_DIR = Fr'{maestro.get_credential(label="RPA", key="dir_rpa")}\{RPA_FULL_NAME}'
RPA_DIR_PRINT = fr'{RPA_DIR}\PRINTS'
RPA_DIR_FILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
RPA_DIR_DOWNLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
EXCECAO_SISTEMA = "Exceção de sistema"
EXCECAO_NEGOCIO = "Exceção de negócio"
SUCESSO = "Sucesso"

# informações referente ao banco de dados do RPA
SERVER_PRD = maestro.get_credential(label="RPA", key="db_rpa_server_prd")
SERVER_HML = maestro.get_credential(label="RPA", key="db_rpa_server_hml")
RPA_DB_SERVER = SERVER_PRD if AMBIENTE_PRODUCAO else SERVER_HML

RPA_DB_NAME = maestro.get_credential(label="RPA", key="db_rpa_database")
RPA_DB_USER = maestro.get_credential(label="RPA", key="db_rpa_user")
RPA_DB_PWD = maestro.get_credential(label="RPA", key="db_rpa_pwd")

# informações referente ao banco de dados do Tasy
HOSTNAME_PRD = maestro.get_credential(label="RPA", key="bd_tasy_hostname_prd")
HOSTNAME_HML = maestro.get_credential(label="RPA", key="bd_tasy_hostname_hml")
TASY_DB_HOSTNAME = HOSTNAME_PRD if AMBIENTE_PRODUCAO else HOSTNAME_HML

SERVICENAME_PRD = maestro.get_credential(label="RPA", key="bd_tasy_service_name_prd")
SERVICENAME_HML = maestro.get_credential(label="RPA", key="bd_tasy_service_name_hml")
TASY_DB_SERVICENAME = SERVICENAME_PRD if AMBIENTE_PRODUCAO else SERVICENAME_HML

TASY_DB_PORT = maestro.get_credential(label="RPA", key="bd_tasy_port")
TASY_DB_USER = maestro.get_credential(label="RPA", key="bd_tasy_user")
TASY_DB_PWD = maestro.get_credential(label="RPA", key="bd_tasy_pwd")

# Variáveis do Tasy Web
if AMBIENTE_PRODUCAO:
    TASY_URL = "https://aproxima.oncoclinicas.com.br"
else:
    TASY_URL = "https://aproxima-hml.oncoclinicas.com.br"

TASY_USER = maestro.get_credential(label=RPA_SHORT_NAME, key="usuario")
TASY_PWD = maestro.get_credential(label=RPA_SHORT_NAME, key="senha")

