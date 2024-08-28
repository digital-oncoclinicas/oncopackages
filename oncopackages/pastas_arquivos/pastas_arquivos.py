from config import RPA_DIR_PRINT, RPA_DIR_DOWNLOADS, LOG_EX_SISTEMA
from oncopackages.banco_dados.rpa import salvar_log_erro
from botcity.web import WebBot
from datetime import datetime
import zipfile
import shutil
import sys
import os


def nova_pasta(caminho: str, substituir_pasta_existente: bool = False):
    """
    Esta função cria uma nova pasta no caminho especificado.
    :param caminho: Caminho da pasta de destino;
    :param substituir_pasta_existente: Se True, substitui a pasta mesmo que ela já existe.
    """

    if substituir_pasta_existente:
        # Apagar a pasta existente
        shutil.rmtree(path=fr"{caminho}", ignore_errors=True)

    # Cria a pasta
    os.makedirs(caminho, exist_ok=True)


def limpar_pasta_prints(quantidade_dias: int = 15):
    """
    Exclui os arquivos da pasta de prints do robô.
    :param quantidade_dias: Arquivos com mais de 'quantidade_dias' serão excluídos.
    """
    mensagem_erro = f"Falha ao excluir arquivos da pasta de prints."
    try:
        # Pegar a data de hoje
        hoje = datetime.today().date()

        # Loop por todos os arquivos da pasta de prints, em ordem decrescente
        for arquivo in os.listdir(RPA_DIR_PRINT):
            # Pega o caminho completo do arquivo
            caminho_arquivo = os.path.join(RPA_DIR_PRINT, arquivo)
            # Se certifica que não se trata de um arquivo temporário
            if os.path.isfile(caminho_arquivo):
                # Pega a data de criação do arquivo
                data_criacao_arquivo = datetime.fromtimestamp(os.stat(caminho_arquivo).st_mtime).date()
                # Se maior que "quantidade_dias" dias, exclui o arquivo
                if (hoje - data_criacao_arquivo).days > quantidade_dias:
                    os.remove(caminho_arquivo)
                else:
                    break
    except:
        error_message = salvar_log_erro(mensagem_erro)
        print(error_message)
        # raise ValueError(error_message)


def compactar_arquivos(arquivos: list, dir_zip: str):
    """
    Realiza a compactação dos arquivos listados.
    :param arquivos: Lista de arquivos a serem compactados;
    :param dir_zip: Diretório onde será salvo o arquivo .zip.
    """
    try:
        # Cria o arquivo .zip
        with zipfile.ZipFile(dir_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Adiciona os arquivos da lista no arquivo .zip
            for arquivo in arquivos:
                nome_arquivo = os.path.basename(arquivo)
                zip_file.write(arquivo, nome_arquivo)

    except Exception:
        error_message = salvar_log_erro("Falha ao compactar os arquivos.")
        raise ValueError(error_message)


def esperar_conclusao_download(bot: WebBot, extensao_arquivo: str = '.pdf', timeout: int = 30000) -> str:
    """
    Espera a conclusão do download do arquivo e retorna o diretório completo dele.
    :param bot: Objeto da BotCity.
    :param extensao_arquivo: Formato do arquivo que será baixado. Exemplo: .pdf, .png, .xlsx...
    :param timeout: tempo máximo de espera pela conclusão do download.
    :return: Diretório completo do arquivo baixado.
    """
    try:
        # Conta a quantidade de arquivos na pasta de downloads com a mesma extensão do arquivo que será baixado
        qt_arquivos_antes = bot.get_file_count(file_extension=extensao_arquivo)

        # Espera a conclusão do download por até timeout segundos
        qt_arquivos_apos = 0
        for i in range(int(timeout / 500)):
            qt_arquivos_apos = bot.get_file_count(file_extension=extensao_arquivo)
            if qt_arquivos_apos > qt_arquivos_antes:
                break
            bot.wait(500)

        if qt_arquivos_apos <= qt_arquivos_antes:
            raise Exception([LOG_EX_SISTEMA, f'Timeout ao esperar a conclusão do download.'])

        # Pega o diretório completo do arquivo baixado
        dir_arquivo = bot.get_last_created_file(path=RPA_DIR_DOWNLOADS)

        return dir_arquivo

    except Exception:
        error_message = salvar_log_erro(f"Falha ao esperar a conclusão do download.", bot)
        raise ValueError(error_message)


def chrome_driver_path():
    """
    Retorna o endereço completo do chromedriver.exe.
    """
    error_messagem = 'Falha capturar o endereço do chromedriver.exe. '
    try:
        pasta_arquivos = sys.prefix + r"\Lib\site-packages\oncopackages\chrome_driver"
        for arquivo in os.listdir(pasta_arquivos):
            if "chromedriver" in arquivo and arquivo.endswith(".exe"):
                dir_chromedriver = os.path.join(pasta_arquivos, arquivo)
                return dir_chromedriver
            elif "chromedriver" in arquivo and arquivo.endswith(".py"):
                caminho_completo = os.path.join(pasta_arquivos, arquivo)
                dir_chromedriver = os.path.splitext(caminho_completo)[0] + '.exe'
                shutil.move(caminho_completo, dir_chromedriver)
                return dir_chromedriver

        raise Exception([LOG_EX_SISTEMA, error_messagem + "Chromedriver.exe não localizado."])

    except Exception:
        error_message = salvar_log_erro(error_messagem)
        raise ValueError(error_message)
