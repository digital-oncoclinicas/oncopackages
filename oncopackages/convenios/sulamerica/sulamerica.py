from oncopackages.ferramentas.web_bot import WebBotOp
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from botcity.web.bot import By


class SulAmerica(WebBotOp):
    def __init__(self, bd_rpa, bd_tasy=None):
        super().__init__(bd_rpa, bd_tasy)

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
            self.navigate_to('https://saude.sulamericaseguros.com.br/prestador/login')
            self.maximize_window()
    
            # Verifica se está na tela de login
            if self.find_element("user", By.ID, waiting_time=5000):
                # Informa o código
                self.find_element("code", By.ID).send_keys(codigo)
                # Informa o usuário
                self.find_element("user", By.ID).send_keys(usuario)
                # Informa o senha
                self.find_element("senha", By.ID).send_keys(senha)
                # Clicar em Entrar
                self.find_element('entrarLogin', By.ID).click()
    
                # Fechar mensagem
                if self.find_element("//*[@id='sas-box-lgpd-info']//button", By.XPATH, ensure_clickable=True,
                                    waiting_time=2000):
                    self.find_element("//*[@id='sas-box-lgpd-info']//button", By.XPATH).click()
    
                # Verificar se o login foi realizado com sucesso
                if self.element_get_text("//p[text()='Usuário ou Senha Inválidos!']", 5) != "":
                    raise Exception(["Excecao_Negocio", "Usuário ou Senha Inválidos."])
                elif self.find_element("//*[@title='Voltar a Home']", By.XPATH, waiting_time=20000):
                    return
                else:
                    raise Exception([LOG_EX_SISTEMA, msg_erro_generica])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(msg_erro_generica, self)
            raise ValueError(error_message)

