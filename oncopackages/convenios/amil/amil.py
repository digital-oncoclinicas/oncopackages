from oncopackages.ferramentas.web_bot import Webbot
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from botcity.web.bot import By


class Amil:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        self.bot = Webbot()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self, usuario: str, senha: str):
        """
        Realiza o login no site do convênio Amil.
        :param usuario: Usuário;
        :param senha: Senha.
        """
        mensagem_erro = "Falha ao realizar login no site da Amil. "
        try:
            # Abre o navegador e acessa o site do convênio
            self.bot.navigate_to("https://credenciado.amil.com.br/login")
    
            # Navegador em tela cheia
            self.bot.maximize_window()
    
            # Espera a tela carregar
            if not self.bot.find_element("login-usuario", By.ID, waiting_time=30000, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Site indisponível."])
    
            # Verificar se o popup com orientações do login está ativo
            if self.bot.find_element("finalizar-walktour", By.ID, waiting_time=1000):
                self.bot.find_element("finalizar-walktour", By.ID).click()
    
            # Informa o usuário
            self.bot.find_element("login-usuario", By.ID, ensure_clickable=True).send_keys(usuario)
    
            # Informa o senha
            self.bot.find_element("login-senha", By.ID).send_keys(senha)
    
            # Entrar
            self.bot.find_element("//button[text()='Entrar']", By.XPATH).click()
    
            # Verificar se o login foi realizado com sucesso
            if self.bot.find_element("//span[contains(text(),'Nome')]", By.XPATH, waiting_time=30000):
                return
    
            # Verificar se a senha está errada
            if self.bot.find_element("//p[text()='Usuário ou senha inválido.']", By.XPATH, waiting_time=0):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Usuário ou senha inválido."])
    
            # Verificar se o Serviço está indisponível no momento.
            if self.bot.find_element("//p[text()='Serviço indisponível no momento.']", By.XPATH, waiting_time=0):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Serviço indisponível no momento."])
    
            # Reportar falha genérica
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

