from config import RPA_SHORT_NAME, LOG_EX_SISTEMA, LOG_EX_NEGOCIO, RPA_DIR_PRINT, LOG_MESSAGES
from multiprocessing import Queue
from botcity.web import WebBot
from datetime import datetime
import logging_loki
import traceback
import logging
import socket
import sys


handler = logging_loki.LokiQueueHandler(
    Queue(-1),
    url="http://192.168.31.128:3100/loki/api/v1/push",
    tags={"application": "error_app"},
    # auth=("username", "password"),
    version="1",
)

logger = logging.getLogger("error_logger")
logger.addHandler(handler)

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

        logger.error(
            msg=traceback.format_exc(),
            extra={"tags": {"SeqErro": nr_seq_erro,
                            "Robo": RPA_SHORT_NAME,
                            "NomeFuncao": function_name,
                            "LinhaErro": error_line,
                            "MensagemErro": error_message,
                            "Runner": socket.gethostname()
                            }
                   }
        )
        return nr_seq_erro

    except:
        error_line = sys.exc_info()[2].tb_lineno
        error_message = sys.exc_info()[1]
        print(f'Falha ao enviar o log para o Grafana Loki - {error_line}:{error_message}')


def salvar_log_erro(bot: [WebBot] = None) -> list:
    """
    Salva log de erro e o print de tela na pasta do robô.
    :param bot: Objeto ou lista de objetos dos navegadores. Usado para tirar o print de tela.
    :return: Lista com [tipo de exceção, mensagem do erro, código do erro]
    """

    # Extrair o nome da função, Linha e Mensagem de erro usando a biblioteca 'sys'
    exc_type, exc_value, exc_traceback = sys.exc_info()
    last_tb = traceback.extract_tb(exc_traceback)[-1]
    # function_path = last_tb.filename
    function_name = last_tb.name
    error_line = last_tb.lineno
    error_message = str(exc_value)
    log_message = LOG_MESSAGES.get(function_name, f"Falha inesperada na função: {function_name}. ")

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
    bot_list = list()
    if isinstance(bot, WebBot):
        bot_list.append(bot)
    elif bot:
        bot_list = bot

    for n, b in enumerate(bot_list):
        if b and b.capabilities:
            if len(bot_list) > 0:
                file_name = fr'{RPA_DIR_PRINT}\{error_seq}_{n}.png'
            else:
                file_name = fr'{RPA_DIR_PRINT}\{error_seq}.png'

            try:
                b.screenshot(file_name)
            except:
                pass

    return error_message
