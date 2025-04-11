from selenium.webdriver.support.select import Select
from oncopackages.ferramentas.web_bot import Webbot
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from botcity.web.bot import By


class Saw:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        self.bot = Webbot()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self, usuario: str, senha: str) -> None:
        """
        Realiza login no site do convênio Central Nacional Unimed
        :param usuario: Usuário;
        :param senha: Senha.
        """
        mensagem_erro = "Falha ao realizar login no site da CNU-SAW. "
        try:    
            # Abre o navegador e acessa o site do convênio
            self.bot.navigate_to("https://saw.trixti.com.br/saw")
    
            # Navegador em tela cheia
            self.bot.maximize_window()
    
            # Informa o usuário
            self.bot.find_element("login", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(usuario)
    
            # Informa o senha
            self.bot.find_element("password", By.ID).send_keys(senha)
    
            # Entrar
            self.bot.enter()
    
            # Verificar se o login foi realizado com sucesso.
            if self.bot.find_element("//label[text()='Principal']", By.XPATH, ensure_visible=True):
                return
            else:  # Às vezes a página cai ao realizar login pela segunda vez. Solução de contorno
                self.bot.navigate_to("https://saw.trixti.com.br/saw")
                if self.bot.find_element("//label[text()='Principal']", By.XPATH, ensure_visible=True):
                    return
    
            # Verificar se a senha está errada
            if (self.bot.find_element("//div[contains(*, 'senha inválida')]", By.XPATH, 0, True)
                    or self.bot.find_element("//div[contains(*, 'Senha incorreta')]", By.XPATH, 0, True)):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Senha/Login Incorreto."])
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)


class Portal:
    def __init__(self, bd_rpa, bd_tasy=None):
        self.bot = Webbot()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy
        
    def login(self, usuario: str, senha: str) -> None:
        """
        Realiza login no portal de serviços On-Line do prestador do convênio Central Nacional Unimed
        :param usuario: Usuário;
        :param senha: Senha.
        """
        mensagem_erro = "Falha ao realizar login no site da CNU-Portal. "
        try:    
            # Abre o navegador e acessa o site do convênio
            self.bot.navigate_to("https://www1.centralnacionalunimed.com.br/psp/menu.jsf")
    
            # Navegador em tela cheia
            self.bot.maximize_window()
    
            # Informa o usuário
            self.bot.find_element("j_username", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(usuario)
    
            # Informa o senha
            self.bot.find_element("j_password", By.ID).send_keys(senha)
    
            # Entrar
            self.bot.enter()
    
            # Verificar se o login foi realizado com sucesso.
            if self.bot.find_element("//a[text()='Sair']", By.XPATH, ensure_visible=True):
                # # Após confirmação do login, o site exibe 4 popups que possuem o mesmo xpath e estão todos visíveis.
                # # Por isso foi necessário especificar o popup pelo ID.
                # # A ordem dos popups muda. Por isso tentamos clicar em todos 3 vezes
                # for n in range(3):
                #     # Popup de alerta 1
                #     self.bot.element_left_click(xpath="//input[@value='Fechar']", tentativas=1, delay=250)
                #     # Popup de alerta 2
                #     self.bot.element_left_click(xpath="//*[@id='frm:btnErrorClose2']", tentativas=1, delay=250)
                #     # Popup de alerta 3
                #     self.bot.element_left_click(xpath="//*[@id='frm:btnMpMsg2']", tentativas=1, delay=250)
                #     # Popup de alerta 4
                #     self.bot.element_left_click(xpath="//*[@id='frm:btnMpMsgERecGlosa']", tentativas=1, delay=250)
    
                return
    
            # Verificar se a senha está errada
            if self.bot.search_element(xpath="//span[contains(text(),'Tente novamente')]", tentativas=1):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Senha/Login Incorreto."])
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)
    
    def consultar_elegibilidade_carteirinha(self,
                                            codigo_prestador: str,
                                            carteirinha: str,
                                            cnu_user: str,
                                            cnu_pwd: str) -> dict:
        """
        Consulta a elegibilidade da carteirinha no site do convênio Central Nacional Unimed.
        :param carteirinha: Carteirinha no paciente;
        :param codigo_prestador: Código do Oncoclínicas no portal;
        :param cnu_user: Usuário do portal da CNU;
        :param cnu_pwd: Senha do portal da CNU.
        :return: Dicionário com a validade da carteirinha e a elegibilidade.
        """
        mensagem_erro = "Falha ao consultar a elegibilidade da carteirinha no portal da CNU. "
        try:
            # O portal da CNU, aleatóriamente realiza o sign out e é necessário realizar sing in novamente.
            for n in range(5):
                # Realiza o login caso necessário
                if not self.bot.capabilities or self.bot.find_element("j_username", By.ID, waiting_time=0):
                    self.login(usuario=cnu_user, senha=cnu_pwd)
    
                # Acessando o menu 'Autorização'
                if not self.bot.search_element(xpath="//*[text()='Elegibilidade']", tentativas=4):
                    self.bot.navigate_to("https://www1.centralnacionalunimed.com.br/auto/blank.jsf")
    
                # Clica no menu 'Elegibilidade'
                if self.bot.element_left_click(xpath="//*[@id='frmMenuElegibilidade']", delay=500):
                    break
    
            if not self.bot.search_element(xpath="//span[text()='Elegibilidade']", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de pesquisa não localizada."])
    
            # Preencher o campo 'Código Prestador:'
            select = Select(self.bot.find_element("frm:selectCodigoPrestador", By.ID))
            select.select_by_visible_text(codigo_prestador)
    
            # No campo 'Código do Cartão:', preencher com a carteirinha e teclar TAB
            self.bot.element_set_text(xpath="//input[@id='frm:cartao']", text=carteirinha)
            self.bot.tab()
    
            # Espera retorno do site
            if not self.bot.search_element(xpath="//input[@value='Imagem da Carteirinha']", tentativas=60):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "O portal não retornou um resultado."])
    
            # Pega validade da carteirinha
            validade = self.bot.element_get_value(xpath="//td[span[text()='Validade do Cartão:']]/input", delay=1000)
    
            # Elegibilidade da carteirinha
            elegibilidade = self.bot.element_get_text(xpath="//tr[11]/td/span", delay=1000)
            if not elegibilidade:
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Resposta do portal não localizada."])
    
            # Pega o retorno do site
            return {'data_validade': validade, 'elegibilidade': elegibilidade}
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

