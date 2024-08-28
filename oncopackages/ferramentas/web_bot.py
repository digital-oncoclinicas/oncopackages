from botcity.web.bot import ActionChains, WebBot, By
from config import LOG_EX_SISTEMA


class WebBotOp(WebBot):
    def __init__(self, bd_rpa, bd_tasy=None):
        super().__init__()
        self.bd_tasy = bd_tasy
        self.bd_rpa = bd_rpa

    def search_element(self, xpath: str, waiting_time: int = 15, delay: int = 0):
        """
        Espera o elemento ficar visível para interagir com ele.
        :param xpath: Xpath do elemento;
        :param waiting_time: Tempo de espera (em segundos);
        :param delay: Tempo de espera após encontrado (em segundos).
        :return: WebElement.
        """
        for n in range(waiting_time):
            try:
                elementos = self.find_elements(xpath, By.XPATH, waiting_time=0, ensure_visible=False)
                for elemento in elementos:
                    if elemento.is_displayed():
                        self.wait(delay)
                        return elemento
            except:
                pass
            self.wait(1000)

        raise Exception(f"Elemento ({xpath}) não localizado.")
        
    def element_click(self, xpath: str, tentativas: int = 30, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e clica nele.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """
        try:
            elemento = self.search_element(xpath, tentativas, delay)
            elemento.click()
            return True
        except:
            return False

    def element_left_click(self, xpath: str, tentativas: int = 30, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e clica nele com o botão esquerdo do mouse.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """
        try:
            elemento = self.search_element(xpath, tentativas, delay)
            action = ActionChains(self.driver)
            action.click(elemento).perform()
            return True
        except:
            return False

    def element_right_click(self, xpath: str, tentativas: int = 30, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e clica nele com o botão direito do mouse.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """
        try:
            elemento = self.search_element(xpath, tentativas, delay)
            action = ActionChains(self.driver)
            action.context_click(elemento).perform()
            return True
        except:
            return False
    
    def element_double_click(self, xpath: str, tentativas: int = 30, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e dá um duplo click nele.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """
        try:
            elemento = self.search_element(xpath, tentativas, delay)
            action = ActionChains(self.driver)
            action.double_click(elemento).perform()
            return True
        except:
            return False
    
    def element_get_text(self, xpath: str, tentativas: int = 30, delay: int = 0) -> str:
        """
        Espera o elemento aparecer e pega o atributo 'text' dele.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de pegar o texto.
        :return: Atributo 'text' do elemento
        """
        try:
            elemento = self.search_element(xpath, tentativas, delay)
            return elemento.text
        except:
            return ''
    
    def element_get_value(self, xpath: str, tentativas: int = 30, delay: int = 0) -> str:
        """
        Espera o elemento aparecer e pega o atributo 'value' dele.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de pegar o texto.
        :return: Atributo 'value' do elemento.
        """
        try:
            elemento = self.search_element(xpath, tentativas, delay)
            return elemento.get_attribute("value")
        except:
            return ''
    
    def element_set_text(self, xpath: str, text: str, tentativas: int = 30, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e insere o valor da variável 'text'.
        :param xpath: XPATH do elemento;
        :param text: Texto a ser inserido no elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de setar o texto.
        :return: True - Se conseguiu inserir o texto no elemento. False se não.
        """
        try:
            elemento = self.search_element(xpath, tentativas, delay)
            elemento.clear()
            elemento.send_keys(text)
            return True
        except:
            return False

    def element_wait_displayed(self, xpath: str, tentativas: int = 30) -> bool:
        """
        Espera o elemento aparecer ficar visível.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas.
        :return: True - Se o elemento for encontrado e ficar visível. False se não.
        """
        try:
            self.search_element(xpath, tentativas)
            return True
        except:
            return False

    def upload_arquivo_background(self,
                                  xpath_upload: str,
                                  caminho_arquivo: str,
                                  xpath_confirmacao: str = None,
                                  timeout: int = 60000) -> bool:
        """
        Realiza o upload de um arquivo sem depender da janela do File Explorer.
    
        Obs: As propriedades ensure_visible e ensure_clickable não foram consideradas,
        pois nem todos os elementos do tipo "file" possuem elas, o que poderia resultar em
        erros indesejados.
    
        :param xpath_upload: XPath para o elemento de upload de arquivo.
        :param caminho_arquivo: Caminho completo para o arquivo a ser carregado.
        :param xpath_confirmacao: (Opcional) XPath para um elemento de verificação.
        :param timeout: Tempo de espera para reportar falha.
        :return: True se o arquivo foi carregado com sucesso.
        """
        error_message = "Falha ao realizar o upload do arquivo. "
        try:
            # Busca pelo elemento web utilizado para realizar upload de arquivo
            self.find_element(xpath_upload, By.XPATH, waiting_time=timeout).send_keys(caminho_arquivo)
    
            # Verifica se um elemento de confirmação de upload foi fornecido
            if xpath_confirmacao:
                # Verifica se o elemento de confirmação existe. Se sim, significa que o upload foi um sucesso.
                if self.find_element(xpath_confirmacao, By.XPATH, waiting_time=timeout, ensure_clickable=True):
                    return True
    
                raise Exception([LOG_EX_SISTEMA, error_message + 'Confirmação do upload não encontrada.'])
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(error_message)
            raise ValueError(error_message)

