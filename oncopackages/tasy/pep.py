from oncopackages.tasy.tasy import Tasy


class ProntuarioEletronicoPaciente(Tasy):

    def selecionar_protocolo(self, protocolo: str) -> None:
        """
        Acessar o menu 'Protocolo de tratamento' e clica no protocolo desejado.
        """
        # Clica no menu 'Protocolo de tratamento'
        xpath = f"//span[contains(text(),'Protocolo de tratamento')]"
        self.bot.search_element(xpath=xpath).click()

        # Clica no protocolo
        xpath = f"//span[contains(text(),'{protocolo}')]"
        self.bot.search_element(xpath=xpath).click()

    def acessar_aba_ciclos(self) -> None:
        """
        Acessar o menu 'Protocolos' -> 'Ciclos'.
        """
        # Clica no menu 'Protocolos'
        xpath = f"//span[contains(text(),'Protocolos')]"
        self.bot.search_element(xpath=xpath).click()

        # Clica no menu 'Ciclos'
        xpath = f"//span[contains(text(),'Ciclos')]"
        self.bot.search_element(xpath=xpath, delay=1000).click()
