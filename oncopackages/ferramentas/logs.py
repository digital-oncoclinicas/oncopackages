from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO, RPA_DIR_PRINT, LOG_MESSAGES, RPA_FULL_NAME
from logging_loki import LokiQueueHandler
from multiprocessing import Queue
from datetime import datetime
import traceback
import logging
import socket
import sys


def get_handler() -> LokiQueueHandler:

    handler = LokiQueueHandler(
        Queue(-1),
        url="http://192.168.31.128:3100/loki/api/v1/push",
        tags={"application": RPA_FULL_NAME},
        # auth=("username", "password"),
        version="1",
    )

    return handler

def __gerar_sequencia_erro(function_name: str, error_line: int, error_message: str):
    """
    Enviar o log de erro para o Grafana Loki.
    :param function_name: Nome da função onde ocorreu o erro;
    :param error_line: Linha onde ocorreu o erro;
    :param error_message: Mensagem do erro.
    :return: Código do erro.
    """
    try:
        nr_seq_erro = datetime.now().strftime("%Y%m%d%H%M%S%f")
        logger = logging.getLogger("error_logger")
        logger.setLevel(logging.ERROR)
        if not logger.handlers:
            logger.addHandler(get_handler())

        logger.error(
            msg=traceback.format_exc(),
            extra={
                "tags": {
                    "nr_seq_erro": nr_seq_erro,
                    "nome_funcao": function_name,
                    "linha_erro": error_line,
                    "mensagem_erro": error_message,
                    "runner": socket.gethostname()
                }
            }
        )

        return nr_seq_erro

    except Exception as error:
        print(f'Falha ao enviar o log para o Grafana Loki - \n{error}')


def salvar_log_erro(bot: object = None) -> list:
    """
    Salva log de erro e o print de tela na pasta do robô.
    :param bot: Objeto do navegador. Usado para tirar o print de tela.
    :return: Lista com [tipo de exceção, mensagem do erro, código do erro]
    """

    # Extrair o nome da função, Linha e Mensagem de erro usando a biblioteca 'sys'
    exc_type, exc_value, exc_traceback = sys.exc_info()
    last_tb = traceback.extract_tb(exc_traceback)[-1]
    # function_path = last_tb.filename
    function_name = last_tb.name
    error_line = last_tb.lineno
    error_message = str(exc_value)
    for tb in traceback.extract_tb(exc_traceback)[::-1]:
        if LOG_MESSAGES.get(tb.name):
            function_name = tb.name
            error_line = tb.lineno
            break
    log_message = LOG_MESSAGES.get(function_name, f"Falha não mapeada. ")

    # Verificar se foi um erro mapeado
    if LOG_EX_SISTEMA in error_message or LOG_EX_NEGOCIO in error_message:  # Erro mapeado
        # Transformar a string em lista
        error_message = eval(error_message)

        # Falha já reportada
        if len(error_message) == 3:
            return error_message

        log_message += error_message[1]
        error_message[1] = log_message
        error_seq = __gerar_sequencia_erro(function_name, error_line, log_message)
        error_message.append(error_seq)

    else:  # Erro não mapeado
        error_seq = __gerar_sequencia_erro(function_name, error_line, error_message)
        error_message = [LOG_EX_SISTEMA, log_message, error_seq]

        # Print de tela caso o objeto bot != None
        try:
            file_name = fr'{RPA_DIR_PRINT}\{error_seq}.png'
            bot.screenshot(file_name)
        except:
            pass

    return error_message
