from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By, Keys
import datetime


class CadastroCompletoPessoas(Tasy):
    
    def acessar_aba_classificacao_paciente(self):
        """
        Acessa a aba 'Classificação do paciente'.
        """
        # Se a opção 'Informação adicional' já estiver selecionada, nada precisa ser feito.
        xpath = "//div[a[ng-include[span[text() = 'Informação adicional']]]]"
        if self.bot.find_element(xpath, By.XPATH, waiting_time=3000, ensure_clickable=True):
            # Já se encontra com a opção correta selecionada
            self.bot.wait(3000)  # Espera necessária para a página carregar completamente
            return

        # Clica no botão 'Complemento' para abrir a lista suspensa.
        # Botão localizado no canto superior esquerdo da segunda tela, acima do label 'Todos complementos'
        xpath = "//div[a[ng-include[span[text() = 'Complemento']]]]"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

        # Seleciona a opção 'Informação adicional'
        xpath = "//a[span[text() = 'Informação adicional']]"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

        # Clica na aba 'Classificações do paciente'
        xpath = "//div[span[contains(text(), 'Classificaçõe')]]"
        if self.bot.find_element(xpath, By.XPATH, waiting_time=3000, ensure_clickable=True):
            self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
        # Se a aba 'Classificações do paciente' não estiver visível
        else:
            # Clicar nos (...) que fica no canto superior direito da segunda tela
            self.bot.find_element('elipsisButton', By.ID, ensure_clickable=True).click()

            # Clica na aba 'Classificações do paciente'
            xpath = "//div[contains(text(), 'Classificaçõe')]"
            self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

            # Clicar nos (...) novamente para ocultar a lista suspensa
            self.bot.find_element('elipsisButton', By.ID, ensure_clickable=True).click()
    
    def atualizar_fim_vigencia(self, observacao: str):
        """
        Atualizar a data fim de vigência de todas as classificações.
        :param observacao: Texto que será adicionado ao campo observação da classificação.
        """
        data_atual = datetime.date.today()
        # Contar a quantidade de linhas que tem na tabela de classificações
        xpath = "//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div"
        qt_classif = len(self.bot.find_elements(xpath, By.XPATH))
        for n in range(0, qt_classif):

            # pega a data fim de vigência
            xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]/div[3]"
            data_fim_vigencia = self.bot.element_get_text(xpath=xpath)
            data_fim_vigencia = data_fim_vigencia.replace('\u202a', '').replace('\u202c', '')
            if data_fim_vigencia != '':
                data_fim_vigencia = datetime.datetime.strptime(data_fim_vigencia, '%d/%m/%Y %H:%M:%S').date()

            if data_fim_vigencia == '' or data_fim_vigencia > data_atual:
                # Clica na linha da tabela
                xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]"
                self.bot.element_click(xpath=xpath, delay=500)

                # Clica em 'Ver'
                if not self.bot.element_click(xpath="//button[span[text() = 'Ver']]", delay=1000):
                    raise Exception([LOG_EX_SISTEMA, "Botão (Ver) não localizado."])

                # Preencher campo 'Fim vigência' com o primeiro dia do mês seguinte ao atual
                data_fim_vigencia = primeiro_dia_mes_seguinte()
                xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
                if not self.bot.element_set_text(xpath=xpath, text=data_fim_vigencia, delay=1000):
                    raise Exception([LOG_EX_SISTEMA, "Campo (Data final de vigência) não localizado."])

                # Preencher campo 'Observação'
                xpath = "//div[div[div[div[contains(text(),'Classificações do paciente')]]]]" \
                        "//textarea[@name='DS_OBSERVACAO']"
                self.bot.find_element(xpath, By.XPATH).clear()
                self.bot.find_element(xpath, By.XPATH).send_keys(observacao)

                # Clica no botão 'Salvar'
                xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
                self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

                # Verifica se salvou com sucesso
                xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]"
                if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
                    raise Exception([LOG_EX_SISTEMA, "Não foi possível confirmar a atualização."])
    
    def adicionar_classificacao_paciente(self, classificacao: str, data_inicio_vigencia: str = '',
                                         data_fim_vigencia: str = ''):
        """
        Informa a Classificação, a data fim de vigência, o campo observação e salva.
        :param classificacao: Classificação do paciente;
        :param data_inicio_vigencia: Data de início da vigência da classificação
        :param data_fim_vigencia: Data fim de vigência.
        """
        # Clica no botão 'Adicionar'
        xpath = "//div[div[div[div[contains(text(), 'Classificações do paciente')]]]]" \
                "//*[contains(text(), 'Adicionar')]"
        if not self.bot.element_click(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])

        # Informa a classificação
        xpath = "//div[div[span[text() = 'Classificação']]]/div[2]/tasy-listbox/div"
        self.bot.element_click(xpath=xpath, delay=500)
        if not self.bot.element_click(xpath=f"//a[span[text() = '{classificacao}']]", delay=500):
            raise Exception([LOG_EX_NEGOCIO, f"Classificação ({classificacao}) não localizada."])

        # Preencher campo 'Início vigência'
        if data_inicio_vigencia != '':
            xpath = "//*[@name= 'DT_INICIO_VIGENCIA']"
            if not self.bot.search_element( xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, "Campo (Início da vigência) não localizado."])
            self.bot.find_element(selector=xpath, by=By.XPATH).click()
            self.bot.type_keys(keys=[Keys.CONTROL, "a"])
            self.bot.kb_type(data_inicio_vigencia)

        # Preencher campo 'Fim vigência'
        if data_fim_vigencia != '':
            xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
            if not self.bot.element_set_text(xpath=xpath, text=data_fim_vigencia, delay=1000):
                raise Exception([LOG_EX_SISTEMA, "Campo (Final vigência) não localizado."])

        # Clica no botão 'Salvar'
        xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

        # Verifica se salvou com sucesso
        if self.bot.search_element(xpath=f"//*[contains(text(), '{classificacao}')]"):
            return

        raise Exception("Adição não confirmada.")
    
    def atualizar_fim_vigencia_classificacao_anterior(self, classif_anterior: str):
        """
        Atualizar a data fim de vigência da classificação anterior.
        :param classif_anterior: Classificação cuja data fim de vigência deve ser atualizada.
        """
        # Verifica se existe a classificação anterior
        xpath = f"//div[div[div[span[contains(text(),'{classif_anterior}')]]]]"
        if not self.bot.find_element(xpath, By.XPATH):
            raise Exception([LOG_EX_NEGOCIO, f"Classificação ({classif_anterior}) não localizada."])

        # Clica na linha da tabela
        self.bot.find_element(xpath, By.XPATH, waiting_time=15000).click()

        # Clica em 'Ver'
        if not self.bot.element_click(xpath="//button[span[text() = 'Ver']]", delay=1000):
            raise Exception([LOG_EX_SISTEMA, "Botão (Ver) não localizado."])

        # Preencher campo 'Fim vigência' com a data de hoje
        data_atual = datetime.datetime.now()
        data_fim_vigencia = data_atual.strftime("%d%m%Y%H%M%S")
        xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
        if not self.bot.element_set_text(xpath=xpath, text=data_fim_vigencia, delay=1000):
            raise Exception([LOG_EX_SISTEMA, "Campo (Data final de vigência) não localizado."])
        data_fim_vigencia = data_atual.strftime("%d/%m/%Y %H:%M:%S")

        # Clica no botão 'Salvar'
        xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
        if self.bot.find_element(xpath, By.XPATH, ensure_clickable=True):
            self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
        else:  # Se o botão 'Salvar' não estiver ativo, clicar em 'Fechar'
            if not self.bot.element_click("//button[span[contains(text(), 'Fechar')]]"):
                raise Exception([LOG_EX_SISTEMA, "Botão (Fechar) não localizado."])

        # Verifica se salvou com sucesso
        xpath = f"//div[div[div[span[contains(text(),'{data_fim_vigencia}')]]]]"
        if self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
            return

        raise Exception("Atualização não confirmada.")
    
    
def primeiro_dia_mes_seguinte() -> str:
    """
    Calcula a data do primeiro dia do mês seguinte ao atual.
    :return: Data do primeiro dia do mês seguinte.
    """
    # Obtém a data atual
    data_atual = datetime.date.today()
    # Obtém o primeiro dia do mês seguinte
    nova_data = data_atual.replace(day=1) + datetime.timedelta(days=32)
    nova_data = nova_data.replace(day=1)
    # Formata a nova data
    nova_data = nova_data.strftime("%d%m%Y") + '235959'

    return nova_data
