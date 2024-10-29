from oncopackages.ferramentas.web_bot import Webbot
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from botcity.web.bot import By


class SulAmerica:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        self.bot = Webbot()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self, usuario: str, senha: str):
        """
        Essa função faz login no site da ULF
        :param usuario: usuário para login no site da ULF
        :param senha: senha para login no site da ULF
        """
    
        # Declaração de Variáveis
        mensagem_erro = 'Falha ao realizar login no site do convênio. '
    
        try:
            # Navegar até a tela de login
            self.bot.navigate_to('https://remote.unimedlestefluminense.coop.br/connecta')
    
            # Tela cheia
            self.bot.maximize_window()
    
            # Verifica se está na tela de login
            if self.bot.find_element("txbUsuario", By.ID, waiting_time=5000):
                # Informa o usuário
                self.bot.find_element("txbUsuario", By.ID).send_keys(usuario)
                # Informa o senha
                self.bot.find_element("txbSenha", By.ID).send_keys(senha)
                # Clicar em Entrar
                self.bot.find_element('btnEntrar', By.ID).click()
    
                # Verificar se o login foi realizado com sucesso
                if self.bot.find_element("cphConteudo_ltvAtalhos_hplAtalho_0", By.ID, waiting_time=20000):
                    return
    
                # Checar mensagem erro
                if self.bot.find_element("modalContentAlert", By.ID, waiting_time=1000):
                    erro = self.bot.find_element("modalContentAlert", By.ID).get_attribute('innerText')
                    if 'usuário e/ou senha estão corretos' in erro:
                        raise Exception([LOG_EX_NEGOCIO, 'Usuário e/ou senha estão incorretos.'])
                    else:
                        raise Exception([LOG_EX_NEGOCIO, f'{mensagem_erro}{erro}'])
    
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

