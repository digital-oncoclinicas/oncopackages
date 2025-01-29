from config import TASY_DB_USER, TASY_DB_PWD, TASY_DB_HOSTNAME, TASY_DB_SERVICENAME
from banco_dados_rpa import BancoDadosRpa
import oracledb


class BancoDadosTasy:
    def __init__(self, bd_rpa: BancoDadosRpa):
        # Conecta com o banco de dados do Tasy
        self.conn = None

        # Criando o cursor
        self.cursor = None

        self.bd_rpa = bd_rpa

    def iniciar_conexao(self):
        # Conecta com o banco de dados do Tasy
        self.conn = oracledb.connect(
            user=TASY_DB_USER,
            password=TASY_DB_PWD,
            dsn=f"{TASY_DB_HOSTNAME}/{TASY_DB_SERVICENAME}"
        )

        # Criando o cursor
        self.cursor = self.conn.cursor()

    def encerrar_conexao(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
