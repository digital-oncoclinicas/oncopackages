from oncopackages.ferramentas.web_bot import WebBotOp
from config import LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from botcity.web.bot import By
import re


class SulAmerica(WebBotOp):
    def __init__(self, bd_rpa, bd_tasy=None):
        super().__init__(bd_rpa, bd_tasy)

    def login(self, usuario: str, senha: str) -> None:
        """
        Realiza login no site do convênio Unimed BH.
        :param usuario: Usuário;
        :param senha: Senha.
        """
        mensagem_erro = "Falha ao realizar login no site da Unimed BH. "
        try:    
            # Abre o navegador e acessa o site do convênio
            self.navigate_to("https://www12.unimedbh.com.br/unioffice/home.do")
    
            # Navegador em tela cheia
            self.maximize_window()
    
            # Informa o usuário
            self.find_element("username", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(usuario)
    
            # Informa o senha
            self.find_element("password", By.ID).send_keys(senha)
    
            # Entrar
            self.enter()
    
            # Verificar se o login foi realizado com sucesso.
            if self.find_element("//td[text()='Página Inicial']", By.XPATH, ensure_visible=True):
                return
    
            # Verificar se a senha está inválida
            if self.find_element("//div[contains(text(),'Credenciais inválidas!')]", By.XPATH, 1000):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Credenciais inválidas!"])
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def consultar_cobertura_beneficiario(self, carteirinha: str) -> dict:
        """
        Consulta a situação e cobertura da elegibilidade de beneficiários Unimed BH.
        :param carteirinha: Carteirinha do paciente.
        :return dicionário com as chaves Produto, Situação, Rede e Tipo de acomodação.
        """
        mensagem_erro = "Falha ao consultar a cobertura do beneficiário. "
        try:
    
            # Acessar a tela de pesquisa
            self.navigate_to("https://www12.unimedbh.com.br/unioffice/conteudoConsultasSituacaoCobertura.do")
    
            # Remove qualquer caractere não numérico
            carteirinha = re.sub(r'[^0-9]', '', carteirinha)
    
            # Preencha com zeros à esquerda até completar 17 caracteres
            carteirinha = carteirinha.zfill(17)
    
            # Preenche o campo Código do beneficiário
            self.find_element("codigo_cliente", By.NAME).send_keys(carteirinha)
            self.enter()
    
            # Deixa a carteirinha com a formatação do site "0.006.0502.982.284.00-0"
            cart_formatada = re.sub(r'(\d)(\d{3})(\d{4})(\d{3})(\d{3})(\d{2})(\d)$', r'\1.\2.\3.\4.\5.\6-\7', carteirinha)
    
            # Verificar se o site localizou o beneficiário
            if not self.find_element(f"//td[contains(text(),'{cart_formatada}')]", By.XPATH):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Beneficiário ({carteirinha}) não localizado."])
    
            produto = self.find_element("//tr[td[contains(text(),'Produto')]]/td[2]", By.XPATH).text
            situacao = self.find_element("//tr[td[contains(text(),'Situação')]]/td[2]", By.XPATH).text
            rede = self.find_element("//tr[td[contains(text(),'Rede')]]/td[2]", By.XPATH).text
            tipo_acomodacao = ""
            xpath = "//tr[td[*[contains(text(),'Tipo de Acomodação')]]]/td[2]"
            if self.find_element(xpath, By.XPATH, waiting_time=100):
                tipo_acomodacao = self.find_element(xpath, By.XPATH).text
    
            return {"Produto": produto,
                    "Situação": situacao,
                    "Rede": rede,
                    "Tipo de acomodação": tipo_acomodacao}
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)

