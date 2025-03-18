from oncopackages.tasy.tasy import Tasy
from config import LOG_EX_SISTEMA
from botcity.web.bot import By


class ProntuarioEletronicoPacienteAmbulatorial(Tasy):
    
    def acessar_consulta(self, dt_fim_consulta: str) -> None:
        """
        Função que seleciona a consulta baseado na data e hora do atendimento
        Args:
            dt_fim_consulta: data fim da consulta no formato DD/MM/YYYY HH:MI;
        """
        # Clica na consulta desejada
        xpath = f"//span[contains(text(),'{dt_fim_consulta}')]"
        if not self.bot.element_click(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, 'Consulta não localizada.'])

        # Valida se a consulta aparece na tabela central
        xpath = f"//div[div[div[span[contains(text(),'{dt_fim_consulta}')]]]]"
        if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
            raise Exception([LOG_EX_SISTEMA, 'Consulta não encontrada.'])

    def selecionar_consulta(self, dt_consulta: str, acessar_consulta: bool = False) -> None:
        """
        Função que seleciona a consulta baseado na data e hora do atendimento
        Args:
            dt_consulta: data da consulta;
            acessar_consulta: boolean que controla se é necessário dar um duplo click na consulta;
        """
        # Seleciona a consulta na tabela central de consultas
        xpath = f"//div[div[div[span[contains(text(),'{dt_consulta}')]]]]"
        if not self.bot.element_click(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, "Consulta não localizada."])

        # Se acessar a consulta estiver com True, dá um duplo click para acessar a consulta selecionada
        if acessar_consulta:
            # Duplo click na primeira linha da tabela de resultados
            if not self.bot.element_double_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, f'Consulta não localizada na tela (data: {dt_consulta}).'])

            return

        # Valida se a tela carregou a conta selecionada (baseado na data fim consulta)
        xpath = f"//div[@id='datagrid']//span[contains(text(),'{dt_consulta}')]"
        if not self.bot.search_element(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, 'Consulta não encontrada na tela após selecionada.'])
