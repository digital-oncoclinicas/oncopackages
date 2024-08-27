from config import TASY_DB_USER, TASY_DB_PWD, TASY_DB_HOSTNAME, TASY_DB_SERVICENAME
from onco_packages.banco_dados.rpa.salvar_log_erro import salvar_log_erro
import oracledb
import time
import sys


def confirmar_taxa_adicionada(nr_sequencia: str) -> bool:
    """
    Espera e confirma se a taxa/bundle/procedimento foi adicionada.
    :param nr_sequencia: Coluna 'NR_SEQUENCIA' da tabela 'TASY.PROCEDIMENTO_PACIENTE'.
    :return True se a taxa foi adicionada, False se a taxa não foi adicionada.
    """
    conn = cursor = None
    mensagem_erro = "Falha ao verificar se a taxa foi adicionada. "
    try:
        # Conecta com o banco de dados do Tasy
        conn = oracledb.connect(user=TASY_DB_USER,
                                password=TASY_DB_PWD,
                                dsn=f"{TASY_DB_HOSTNAME}/{TASY_DB_SERVICENAME}")

        # Criando o cursor
        cursor = conn.cursor()

        query = f"""
        SELECT * 
        FROM TASY.PROCEDIMENTO_PACIENTE
        WHERE NR_SEQUENCIA = :NR_SEQUENCIA
        """

        taxa_adicionada = False
        contador = 0
        while contador <= 10:
            # Executa a consulta no banco de dados
            cursor.execute(query, NR_SEQUENCIA=nr_sequencia)

            # Pega o resultado da consulta
            row = cursor.fetchone()
            if row:
                taxa_adicionada = True
                break
            contador += 1
            time.sleep(1)

        return taxa_adicionada

    except:
        error_message = salvar_log_erro(sys, mensagem_erro)
        raise ValueError(error_message)

    finally:
        # Fecha o cursor
        if cursor is not None:
            cursor.close()
        # Encerra a conexão com o banco de dados
        if conn is not None:
            conn.close()

