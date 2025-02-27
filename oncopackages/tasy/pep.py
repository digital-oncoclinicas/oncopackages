from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from oncopackages.tasy.tasy import Tasy


class ProntuarioEletronicoPaciente(Tasy):
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        super().__init__(bd_rpa, bd_tasy)
    
    def selecionar_protocolo(self, protocolo: str) -> None:
        """
        Acessar o menu 'Protocolo de tratamento' e clica no protocolo desejado.
        """
        mensagem_erro = 'Falha ao acessar o protocolo. '
        try:
            # Clica no menu 'Protocolo de tratamento'
            xpath = f"//span[contains(text(),'Protocolo de tratamento')]"
            self.bot.search_element(xpath=xpath).click()

            # Clica no protocolo
            xpath = f"//span[contains(text(),'{protocolo}')]"
            self.bot.search_element(xpath=xpath).click()
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def acessar_aba_ciclos(self) -> None:
        """
        Acessar o menu 'Protocolos' -> 'Ciclos'.
        """
        mensagem_erro = 'Falha ao acessar a aba ciclos. '
        try:
            # Clica no menu 'Protocolos'
            xpath = f"//span[contains(text(),'Protocolos')]"
            self.bot.search_element(xpath=xpath).click()

            # Clica no menu 'Ciclos'
            xpath = f"//span[contains(text(),'Ciclos')]"
            self.bot.element_click(xpath=xpath, delay=1000)

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)
