from config import (RPA_DB_NAME, RPA_DB_USER, RPA_DB_SERVER, RPA_DB_PWD, RPA_SHORT_NAME, LOG_EX_SISTEMA,
                    LOG_EX_NEGOCIO, RPA_DIR_PRINT, LOG_MESSAGES)
import traceback
import pyodbc
import socket
import sys


class BancoDadosRpa:
    def __init__(self):
        # Conecta com o banco de dados
        self.conn = pyodbc.connect(
            'Driver={SQL Server};'
            f'Server={RPA_DB_SERVER};'
            f'Database={RPA_DB_NAME};'
            f'UID={RPA_DB_USER};'
            f'PWD={RPA_DB_PWD};')

        # Cria o cursor
        self.cursor = self.conn.cursor()

    def __gerar_sequencia_erro(self, function_name: str, error_line: int, error_message: str):
        """
        Executa a procedure 'INSERIR_LOG_ERRO' do banco de dados do robô.
        :param function_name: Nome da função que está sendo executada;
        :param error_line: Linha em que o erro ocorreu;
        :param error_message: Mensagem do erro.
        :return: Código do erro.
        """
        try:
            # Montando a query sql para execução da procedure
            query = """
                DECLARE @Out int;
                EXEC [RPA].[INSERIR_LOG_ERRO] 
                    @rpa = ?, 
                    @taskName = ?, 
                    @errorlineNumber = ?, 
                    @errorMessage = ?, 
                    @runner = ?, 
                    @traceback = ?, 
                    @nrSequencia = @Out OUTPUT;
                SELECT @Out;
            """

            # Criando lista de parâmetros de entrada da procedure
            error_message = str(error_message).replace("'", "")
            runner = socket.gethostname()
            traceback_info = traceback.format_exc().replace("'", "")
            parametros = (RPA_SHORT_NAME, function_name, error_line, error_message, runner , traceback_info)

            # Executando a procedure
            self.cursor.execute(query, parametros)

            # Pegando o valor de retorno
            row = self.cursor.fetchone()
            nr_seq_erro = row[0]

            # Salva as alterações
            self.conn.commit()

            return nr_seq_erro

        except:
            error_line = sys.exc_info()[2].tb_lineno
            error_message = sys.exc_info()[1]
            print(f'Falha ao salvar o log de erro no banco de dados - {error_line}:{error_message}')

    def salvar_log_erro(self, bot: object|list[object] = None) -> list:
        """
        Salva log de erro no banco de dados e o print de tela na pasta do robô.
        :param bot: Objeto do navegador usado para tirar o print de tela.
        :return: Lista com [tipo de exceção, mensagem do erro, código do erro]
        """

        # Extrair o nome da função, Linha e Mensagem de erro usando a biblioteca 'sys'
        exc_type, exc_value, exc_traceback = sys.exc_info()
        last_tb = traceback.extract_tb(exc_traceback)[-1]
        # function_path = last_tb.filename
        function_name = last_tb.name
        error_line = last_tb.lineno
        error_message = str(exc_value)
        log_message = LOG_MESSAGES.get(function_name, f"Falha inesperada na função: {function_name}")

        # Verificar se foi um erro mapeado
        if LOG_EX_SISTEMA in error_message or LOG_EX_NEGOCIO in error_message:  # Erro mapeado
            # Transformar a string em lista
            error_message = eval(error_message)

            # Falha já reportada
            if len(error_message) == 3:
                return error_message

            log_message += error_message[1]
            error_message[1] = log_message
            error_seq = self.__gerar_sequencia_erro(function_name, error_line, log_message)
            error_message.append(error_seq)

        else:  # Erro não mapeado
            error_seq = self.__gerar_sequencia_erro(function_name, error_line, error_message)
            error_message = [LOG_EX_SISTEMA, log_message, error_seq]

        # Print de tela caso o objeto bot != None
        bot_list = list()
        if isinstance(bot, list):
            bot_list = bot
        elif bot:
            bot_list.append(bot)

        for n, b in enumerate(bot_list):
            if len(bot_list) > 1:
                file_name = fr'{RPA_DIR_PRINT}\{error_seq}_{n}.png'
            else:
                file_name = fr'{RPA_DIR_PRINT}\{error_seq}.png'

            try:
                b.screenshot(file_name)
            except:
                pass

        return error_message

    def encerrar_conexao(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
