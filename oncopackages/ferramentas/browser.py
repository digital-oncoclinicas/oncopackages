from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from config import LOG_EX_SISTEMA
from selenium import webdriver
import time


class Browser(webdriver.Chrome):
    def __init__(self, driver: webdriver.Chrome):
        super().__init__()
        self.driver = driver

    def search_element(self, by, selector: str, waiting_time: int = 15, delay: int = 0):
        """
        Espera o elemento ficar visível para interagir com ele.
        :param by: Localizador
        :param selector: Seletor;
        :param waiting_time: Tempo de espera (em segundos);
        :param delay: Tempo de espera após encontrado (em segundos).
        :return: WebElement.
        """

        for n in range(waiting_time):
            try:
                elementos = self.driver.find_elements(by, selector)
                for elemento in elementos:
                    if elemento.is_displayed():
                        time.sleep(delay)
                        return elemento
            except:
                pass
            time.sleep(1)

        raise NoSuchElementException("Cannot locate relative element")

    def element_click(self, by: By, selector: str, waiting_time: int = 15, delay: int = 0) -> bool:
        """
        Espera o elemento ficar visível e clica nele.
        :param by: Localizador
        :param selector: Seletor;
        :param waiting_time: Tempo de espera (em segundos);
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """

        for n in range(waiting_time):
            try:
                elementos = self.driver.find_elements(by, selector)
                for elemento in elementos:
                    if elemento.is_displayed():
                        try:
                            time.sleep(delay)
                            elemento.click()
                            return True
                        except:
                            pass
            except:
                pass
            time.sleep(1)
        return False

    def element_left_click(self, by: By, selector: str, waiting_time: int = 15, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e clica nele com o botão esquerdo do mouse.
        :param by: Localizador
        :param selector: Seletor;
        :param waiting_time: Tempo de espera (em segundos);
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """

        for n in range(waiting_time):
            try:
                elementos = self.driver.find_elements(by, selector)
                for elemento in elementos:
                    if elemento.is_displayed():
                        try:
                            time.sleep(delay)
                            action = ActionChains(self.driver)
                            action.click(elemento).perform()
                            return True
                        except:
                            pass
            except:
                pass
            time.sleep(1)
        return False

    def element_right_click(self, by: By, selector: str, waiting_time: int = 15, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e clica nele com o botão direito do mouse.
        :param by: Localizador
        :param selector: Seletor;
        :param waiting_time: Tempo de espera (em segundos);
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """

        for n in range(waiting_time):
            try:
                elementos = self.driver.find_elements(by, selector)
                for elemento in elementos:
                    if elemento.is_displayed():
                        try:
                            time.sleep(delay)
                            action = ActionChains(self.driver)
                            action.context_click(elemento).perform()
                            return True
                        except:
                            pass
            except:
                pass
            time.sleep(1)
        return False

    def element_double_click(self, by: By, selector: str, waiting_time: int = 15, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e dá um duplo click nele.
        :param by: Localizador
        :param selector: Seletor;
        :param waiting_time: Tempo de espera (em segundos);
        :param delay: Tempo de espera antes de clicar.
        :return: True - Se conseguiu clicar no elemento. False se não.
        """

        for n in range(waiting_time):
            try:
                elementos = self.driver.find_elements(by, selector)
                for elemento in elementos:
                    if elemento.is_displayed():
                        try:
                            time.sleep(delay)
                            action = ActionChains(self.driver)
                            action.double_click(elemento).perform()
                            return True
                        except:
                            pass
            except:
                pass
            time.sleep(1)
        return False

    def element_displayed(self, by: By, selector: str, waiting_time: int = 15) -> bool:
        """
        Espera o elemento aparecer ficar visível.
        :param by: Localizador;
        :param selector: Seletor;
        :param waiting_time: Tempo de espera (em segundos);
        :return: True - Se o elemento for encontrado e ficar visível. False se não.
        """

        for n in range(waiting_time):
            try:
                elementos = self.driver.find_elements(by, selector)
                for elemento in elementos:
                    if elemento.is_displayed():
                        return True
            except:
                pass
            time.sleep(1)
        return False
    
    def element_set_text(self, by: By, selector: str, text: str, waiting_time: int = 15, delay: int = 0) -> bool:
        """
        Espera o elemento aparecer e insere o valor da variável 'text'.
        :param by: Localizador;
        :param selector: Seletor;
        :param text: Texto que será escrito no elemento;
        :param waiting_time: Tempo de espera (em segundos);
        :param delay: Tempo de espera antes de pegar o texto (em segundos).
        :return: True - Se conseguiu inserir o texto no elemento. False se não.
        """
        for n in range(waiting_time):
            try:
                elementos = self.driver.find_elements(by, selector)
                for elemento in elementos:
                    if elemento.is_displayed():
                        time.sleep(delay)
                        elemento.clear()
                        elemento.send_keys(text)
                        return True
            except:
                pass
            time.sleep(1)

        return False

    def upload_arquivo_background(self, xpath_upload: str, caminho_arquivo: str, xpath_confirmacao: str = None):
        """
        Realiza o upload de um arquivo sem depender da janela do File Explorer.
        :param xpath_upload: XPath para o elemento de upload de arquivo.
        :param caminho_arquivo: Caminho completo para o arquivo a ser carregado.
        :param xpath_confirmacao: (Opcional) XPath para um elemento de verificação.
        """
        # Busca pelo elemento web utilizado para realizar upload de arquivo
        self.find_element(By.XPATH, xpath_upload).send_keys(caminho_arquivo)

        # Verifica se um elemento de confirmação de upload foi fornecido
        if xpath_confirmacao:
            # Verifica se o elemento de confirmação existe. Se sim, significa que o upload foi um sucesso.
            if self.driver.find_element(By.XPATH, xpath_confirmacao):
                return

            error_message = "Falha ao realizar o upload do arquivo. Confirmação do upload não encontrada."
            raise Exception([LOG_EX_SISTEMA, error_message])

    def type_keys(self, keys: list, interval: int = 0):

        action = ActionChains(self.driver)

        for k in keys:
            action.key_down(k)
            action.pause(interval)
        for k in reversed(keys):
            action.key_up(k)
            action.pause(interval)
        action.perform()
