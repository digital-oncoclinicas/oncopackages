from config import RPA_DIR_PRINT
from datetime import datetime
import zipfile
import shutil
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
    except Exception as error:
        print(str(error))


def compactar_arquivos(arquivos: list, dir_zip: str):
    """
    Realiza a compactação dos arquivos listados.
    :param arquivos: Lista de arquivos a serem compactados;
    :param dir_zip: Diretório onde será salvo o arquivo .zip.
    """
    # Cria o arquivo .zip
    with zipfile.ZipFile(dir_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Adiciona os arquivos da lista no arquivo .zip
        for arquivo in arquivos:
            nome_arquivo = os.path.basename(arquivo)
            zip_file.write(arquivo, nome_arquivo)
