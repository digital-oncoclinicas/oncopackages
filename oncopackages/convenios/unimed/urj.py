from oncopackages.ferramentas.web_bot import WebBotOp
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from botcity.web.bot import By


class Urj(WebBotOp):
    def __init__(self, bd_rpa, bd_tasy=None):
        super().__init__(bd_rpa, bd_tasy)

    def login(self, usuario: str, senha: str) -> None:
        """
        Essa função faz login no site da Unimed Rio.
        :param usuario: Usuário;
        :param senha: Senha.
        """
        mensagem_erro = 'Falha ao realizar login no site do convênio. '
        try:    
            # Abre o navegador e acessa o site do convênio
            self.navigate_to("https://producaoonline.unimedrio.com.br/prestador/Home/Index")
    
            # Navegador em tela cheia
            self.maximize_window()
    
            # Fechar pop-ups
            xpath = "//button[text()='Ok']"
            self.element_click(xpath=xpath, tentativas=5)
    
            # Informa o usuário
            self.find_element("login", By.ID, waiting_time=20000, ensure_clickable=True).send_keys(usuario)
    
            # Informa o senha
            self.find_element("pass", By.ID).send_keys(senha)
    
            # Entrar
            self.enter()
    
            # Verificar se a senha está incorreta
            if self.find_element("//*[contains(text(), 'A senha informada está incorreta.')]", By.XPATH, waiting_time=1000):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Usuário ou senha inválidos."])
    
            # Verificar se o login foi realizado com sucesso
            if self.find_element("//a[contains(text(), 'Home')]", By.XPATH, waiting_time=20000):
                return
    
            # Reportar falha genérica
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)

