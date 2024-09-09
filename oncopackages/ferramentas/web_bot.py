from config import RPA_DIR_DOWNLOADS, HEADLESS, LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from botcity.web.bot import ActionChains, WebBot, By
import shutil
import sys
import os


class WebBotOp(WebBot):
    def __init__(self, bd_rpa, bd_tasy=None):
        super().__init__()

        self.bd_tasy = bd_tasy
        self.bd_rpa = bd_rpa

        # Define se o navegador vai ficar visível ou não
        self.headless = HEADLESS

        # Define a pasta usada para salvar os downloads
        self.download_folder_path = RPA_DIR_DOWNLOADS

        # Define o diretório do chromedriver.exe. Baixado do onco_packages
        self.driver_path = self.chrome_driver_path()

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
        
    def element_click(self, xpath: str, tentativas: int = 15, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e clica nele.
        :param xpath: XPATH do elemento;
        :param tentativas: Número de tentativas;
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """
        for n in range(tentativas):
            try:
                elementos = self.find_elements(xpath, By.XPATH, waiting_time=0, ensure_visible=False)
                for elemento in elementos:
                    if elemento.is_displayed():
                        self.wait(delay)
                        elemento.click()
                        return True
            except:
                pass
            self.wait(1000)

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

    def esperar_conclusao_download(self, extensao_arquivo: str = '.pdf', timeout: int = 30000) -> str:
        """
        Espera a conclusão do download do arquivo e retorna o diretório completo dele.
        :param extensao_arquivo: Formato do arquivo que será baixado. Exemplo: .pdf, .png, .xlsx...
        :param timeout: tempo máximo de espera pela conclusão do download.
        :return: Diretório completo do arquivo baixado.
        """
        try:
            # Conta a quantidade de arquivos na pasta de downloads com a mesma extensão do arquivo que será baixado
            qt_arquivos_antes = self.get_file_count(file_extension=extensao_arquivo)

            # Espera a conclusão do download por até timeout segundos
            qt_arquivos_apos = 0
            for i in range(int(timeout / 500)):
                qt_arquivos_apos = self.get_file_count(file_extension=extensao_arquivo)
                if qt_arquivos_apos > qt_arquivos_antes:
                    break
                self.wait(500)

            if qt_arquivos_apos <= qt_arquivos_antes:
                raise Exception([LOG_EX_SISTEMA, f'Timeout ao esperar a conclusão do download.'])

            # Pega o diretório completo do arquivo baixado
            dir_arquivo = self.get_last_created_file(path=RPA_DIR_DOWNLOADS)

            return dir_arquivo

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(f"Falha ao esperar a conclusão do download.", self)
            raise ValueError(error_message)

    def chrome_driver_path(self):
        """
        Retorna o endereço completo do chromedriver.exe.
        """
        error_messagem = 'Falha capturar o endereço do chromedriver.exe. '
        try:
            pasta_arquivos = sys.prefix + r"\Lib\site-packages\oncopackages\chrome_driver"
            for arquivo in os.listdir(pasta_arquivos):
                if "chromedriver" in arquivo and arquivo.endswith(".exe"):
                    dir_chromedriver = os.path.join(pasta_arquivos, arquivo)
                    return dir_chromedriver
                elif "chromedriver" in arquivo and arquivo.endswith(".py"):
                    caminho_completo = os.path.join(pasta_arquivos, arquivo)
                    dir_chromedriver = os.path.splitext(caminho_completo)[0] + '.exe'
                    shutil.move(caminho_completo, dir_chromedriver)
                    return dir_chromedriver

            raise Exception([LOG_EX_SISTEMA, error_messagem + "Chromedriver.exe não localizado."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(error_messagem)
            raise ValueError(error_message)

