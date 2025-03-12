from config import TASY_DB_USER, TASY_DB_PWD, TASY_DB_HOSTNAME, TASY_DB_SERVICENAME
import oracledb


class BancoDadosTasy:
    def __init__(self):
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
