from oncopackages.ferramentas.web_bot import Webbot
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from botcity.web.bot import By


class Ubh:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        self.bot = Webbot()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self, usuario: str, senha: str) -> None:
        """
        Realiza login no site do convênio Unimed BH.
        :param usuario: Usuário;
        :param senha: Senha.
        """
        mensagem_erro = "Falha ao realizar login no site da Unimed BH. "
        try:    
            # Abre o navegador e acessa o site do convênio
            self.bot.navigate_to("https://www12.unimedbh.com.br/unioffice/home.do")

            # Navegador em tela cheia
            self.bot.maximize_window()

            # Informa o usuário
            self.bot.find_element("username", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(usuario)

            # Informa o senha
            self.bot.find_element("password", By.ID).send_keys(senha)

            # Entrar
            self.bot.enter()

            # Verificar se o login foi realizado com sucesso.
            if self.bot.find_element("//td[text()='Página Inicial']", By.XPATH, ensure_visible=True):
                return

            # Verificar se a senha está inválida
            if self.bot.find_element("//div[contains(text(),'Credenciais inválidas!')]", By.XPATH, 1000):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Credenciais inválidas!"])

            # Reportar falha genérica
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)
