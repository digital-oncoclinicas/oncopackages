from oncopackages.ferramentas.browser import Browser
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from config import LOG_EX_SISTEMA
from botcity.web.bot import By


class SulAmerica:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        self.bot = Browser()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self, codigo: str, usuario: str, senha: str):
        """
        Essa função faz login no site da Sul America
        :param codigo: Código do operador
        :param usuario: Usuário de acesso ao site da sulamerica
        :param senha: Senha de acesso ao site da sulamerica
        """
        msg_erro_generica = 'Falha ao realizar login no site do convênio. '
        try:    
            # Navegar em tela cheia
            self.bot.navigate_to('https://saude.sulamericaseguros.com.br/prestador/login')
            self.bot.maximize_window()
    
            # Verifica se está na tela de login
            if self.bot.find_element("user", By.ID, waiting_time=5000):
                # Informa o código
                self.bot.find_element("code", By.ID).send_keys(codigo)
                # Informa o usuário
                self.bot.find_element("user", By.ID).send_keys(usuario)
                # Informa o senha
                self.bot.find_element("senha", By.ID).send_keys(senha)
                # Clicar em Entrar
                self.bot.find_element('entrarLogin', By.ID).click()
    
                # Fechar mensagem
                if self.bot.find_element("//*[@id='sas-box-lgpd-info']//button", By.XPATH, ensure_clickable=True,
                                    waiting_time=2000):
                    self.bot.find_element("//*[@id='sas-box-lgpd-info']//button", By.XPATH).click()
    
                # Verificar se o login foi realizado com sucesso
                if self.bot.element_get_text("//p[text()='Usuário ou Senha Inválidos!']", 5) != "":
                    raise Exception(["Excecao_Negocio", "Usuário ou Senha Inválidos."])
                elif self.bot.find_element("//*[@title='Voltar a Home']", By.XPATH, waiting_time=20000):
                    return
                else:
                    raise Exception([LOG_EX_SISTEMA, msg_erro_generica])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(msg_erro_generica, self.bot)
            raise ValueError(error_message)

