from oncopackages.ferramentas.web_bot import Webbot
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from botcity.web.bot import By


class Urj:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        self.bot = Webbot()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self, usuario: str, senha: str) -> None:
        """
        Essa função faz login no site da Unimed Rio.
        :param usuario: Usuário;
        :param senha: Senha.
        """
        mensagem_erro = 'Falha ao realizar login no site do convênio. '
        try:    
            # Abre o navegador e acessa o site do convênio
            self.bot.navigate_to("https://producaoonline.unimedrio.com.br/prestador/Home/Index")
    
            # Navegador em tela cheia
            self.bot.maximize_window()
    
            # Fechar pop-ups
            xpath = "//button[text()='Ok']"
            self.bot.element_click(xpath=xpath, tentativas=5)
    
            # Informa o usuário
            self.bot.find_element("login", By.ID, waiting_time=20000, ensure_clickable=True).send_keys(usuario)
    
            # Informa o senha
            self.bot.find_element("pass", By.ID).send_keys(senha)
    
            # Entrar
            self.bot.enter()
    
            # Verificar se a senha está incorreta
            if self.bot.find_element("//*[contains(text(), 'A senha informada está incorreta.')]", By.XPATH, waiting_time=1000):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Usuário ou senha inválidos."])
    
            # Verificar se o login foi realizado com sucesso
            if self.bot.find_element("//a[contains(text(), 'Home')]", By.XPATH, waiting_time=20000):
                return
    
            # Reportar falha genérica
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

