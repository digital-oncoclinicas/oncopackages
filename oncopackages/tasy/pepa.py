from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from oncopackages.tasy.tasy import Tasy
from config import LOG_EX_SISTEMA
from botcity.web.bot import By


class ProntuarioEletronicoPacienteAmbulatorial(Tasy):
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        super().__init__(bd_rpa, bd_tasy)
    
    def acessar_consulta(self, dt_fim_consulta: str) -> None:
        """
        Função que seleciona a consulta baseado na data e hora do atendimento
        Args:
            dt_fim_consulta: data fim da consulta no formato DD/MM/YYYY HH:MI;
        """
        mensagem_erro = 'Falha ao acessar a consulta no PEPA. '
        try:
            # Clica na consulta desejada
            xpath = f"//span[contains(text(),'{dt_fim_consulta}')]"
            if not self.bot.element_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + 'Consulta não localizada.'])
    
            # Valida se a consulta aparece na tabela central
            xpath = f"//div[div[div[span[contains(text(),'{dt_fim_consulta}')]]]]"
            if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, 'Consulta não encontrada.'])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)
