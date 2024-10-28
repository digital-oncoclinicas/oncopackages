from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By, Keys
import datetime
import time


class CadastroCompletoPessoas(Tasy):
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        super().__init__(bd_rpa, bd_tasy)
    
    def acessar_aba_classificacao_paciente(self):
        """
        Acessa a aba 'Classificação do paciente'.
        """
        mensagem_erro = "Falha ao acessar a aba Classificação do Paciente. "
        try:
            # Se a opção 'Informação adicional' já estiver selecionada, nada precisa ser feito.
            xpath = "//div[a[ng-include[span[text() = 'Informação adicional']]]]"
            if self.browser.search_element(By.XPATH, xpath, waiting_time=3):
                # Já se encontra com a opção correta selecionada
                time.sleep(3)  # Espera necessária para a página carregar completamente
                return
    
            # Clica no botão 'Complemento' para abrir a lista suspensa.
            # Botão localizado no canto superior esquerdo da segunda tela, acima do label 'Todos complementos'
            xpath = "//div[a[ng-include[span[text() = 'Complemento']]]]"
            self.browser.search_element(By.XPATH, xpath).click()
    
            # Seleciona a opção 'Informação adicional'
            xpath = "//a[span[text() = 'Informação adicional']]"
            self.browser.search_element(By.XPATH, xpath).click()
    
            # Clica na aba 'Classificações do paciente'
            xpath = "//div[span[contains(text(), 'Classificaçõe')]]"
            if self.browser.search_element(By.XPATH, xpath, waiting_time=3):
                self.browser.search_element(By.XPATH, xpath).click()
            # Se a aba 'Classificações do paciente' não estiver visível
            else:
                # Clicar nos (...) que fica no canto superior direito da segunda tela
                self.browser.search_element(By.ID, 'elipsisButton').click()
    
                # Clica na aba 'Classificações do paciente'
                xpath = "//div[contains(text(), 'Classificaçõe')]"
                self.browser.search_element(By.XPATH, xpath).click()
    
                # Clicar nos (...) novamente para ocultar a lista suspensa
                self.browser.search_element(By.ID, 'elipsisButton').click()
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)
    
    def atualizar_fim_vigencia(self, observacao: str):
        """
        Atualizar a data fim de vigência de todas as classificações.
        :param observacao: Texto que será adicionado ao campo observação da classificação.
        """
        mensagem_erro = "Falha ao atualizar a data fim de vigência. "
        data_atual = datetime.date.today()
        try:
            # Contar a quantidade de linhas que tem na tabela de classificações
            xpath = "//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div"
            qt_classif = len(self.browser.find_elements(By.XPATH, xpath))
            for n in range(0, qt_classif):
    
                # pega a data fim de vigência
                xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]/div[3]"
                data_fim_vigencia = self.browser.element_get_text(By.XPATH, xpath)
                data_fim_vigencia = data_fim_vigencia.replace('\u202a', '').replace('\u202c', '')
                if data_fim_vigencia != '':
                    data_fim_vigencia = datetime.datetime.strptime(data_fim_vigencia, '%d/%m/%Y %H:%M:%S').date()
    
                if data_fim_vigencia == '' or data_fim_vigencia > data_atual:
                    # Clica na linha da tabela
                    xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]"
                    self.browser.element_click(By.XPATH, xpath, delay=1)
    
                    # Clica em 'Ver'
                    if not self.browser.element_click(By.XPATH, "//button[span[text() = 'Ver']]", delay=1):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Ver) não localizado."])
    
                    # Preencher campo 'Fim vigência' com o primeiro dia do mês seguinte ao atual
                    data_fim_vigencia = primeiro_dia_mes_seguinte()
                    xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
                    if not self.browser.element_set_text(By.XPATH, xpath, text=data_fim_vigencia, delay=1):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo (Data final de vigência) não localizado."])
    
                    # Preencher campo 'Observação'
                    xpath = "//div[div[div[div[contains(text(),'Classificações do paciente')]]]]" \
                            "//textarea[@name='DS_OBSERVACAO']"
                    self.browser.search_element(By.XPATH, xpath).clear()
                    self.browser.search_element(By.XPATH, xpath).send_keys(observacao)
    
                    # Clica no botão 'Salvar'
                    xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
                    self.browser.search_element(By.XPATH, xpath).click()
    
                    # Verifica se salvou com sucesso
                    xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]"
                    if not self.browser.search_element(By.XPATH, xpath):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível confirmar a atualização."])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)
    
    def adicionar_classificacao_paciente(self, classificacao: str, data_fim_vigencia: str = '',
                                         data_inicio_vigencia: str = ''):
        """
        Informa a Classificação, a data fim de vigência, o campo observação e salva.
        :param classificacao: Classificação do paciente;
        :param data_inicio_vigencia: Data de início da vigência da classificação
        :param data_fim_vigencia: Data fim de vigência.
        """
        mensagem_erro = "Falha ao adicionar classificação do paciente. "
        try:
            # Clica no botão 'Adicionar'
            xpath = "//div[div[div[div[contains(text(), 'Classificações do paciente')]]]]" \
                    "//*[contains(text(), 'Adicionar')]"
            if not self.browser.element_click(By.XPATH, xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])
    
            # Informa a classificação
            xpath = "//div[div[span[text() = 'Classificação']]]/div[2]/tasy-listbox/div"
            self.browser.element_click(By.XPATH, xpath, delay=1)
            if not self.browser.element_click(By.XPATH, f"//a[span[text() = '{classificacao}']]", delay=1):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Classificação ({classificacao}) não localizada."])
    
            # Preencher campo 'Início vigência'
            if data_inicio_vigencia != '':
                xpath = "//*[@name= 'DT_INICIO_VIGENCIA']"
                if not self.browser.element_displayed(By.XPATH, xpath):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo (Início da vigência) não localizado."])
                self.browser.search_element(By.XPATH, xpath).click()
                self.browser.type_keys(keys=[Keys.CONTROL, "a"])
                self.browser.search_element(By.XPATH, xpath).send_keys(data_inicio_vigencia)
    
            # Preencher campo 'Fim vigência'
            if data_fim_vigencia != '':
                xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
                if not self.browser.element_set_text(By.XPATH, xpath, text=data_fim_vigencia, delay=1):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo (Final vigência) não localizado."])
    
            # Clica no botão 'Salvar'
            xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
            self.browser.search_element(By.XPATH, xpath).click()
    
            # Verifica se salvou com sucesso
            xpath = f"(//div[contains(@data-row-idx, '0')])[2]"
            if self.browser.search_element(By.XPATH, xpath):
                return
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)
    
    def atualizar_fim_vigencia_classificacao_anterior(self, classif_anterior: str):
        """
        Atualizar a data fim de vigência da classificação anterior.
        :param classif_anterior: Classificação cuja data fim de vigência deve ser atualizada.
        """
        mensagem_erro = "Falha ao atualizar a data fim de vigência da classificação anterior. "
        try:
            # Verifica se existe a classificação anterior
            xpath = f"//div[div[div[span[contains(text(),'{classif_anterior}')]]]]"
            if not self.browser.search_element(By.XPATH, xpath):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Classificação ({classif_anterior}) não localizada."])
    
            # Clica na linha da tabela
            self.browser.search_element(By.XPATH, xpath).click()
    
            # Clica em 'Ver'
            if not self.browser.element_click(By.XPATH, "//button[span[text() = 'Ver']]", delay=1):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Ver) não localizado."])
    
            # Preencher campo 'Fim vigência' com a data de hoje
            data_atual = datetime.datetime.now()
            data_fim_vigencia = data_atual.strftime("%d%m%Y%H%M%S")
            xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
            if not self.browser.element_set_text(By.XPATH, xpath, text=data_fim_vigencia, delay=1):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo (Data final de vigência) não localizado."])
            data_fim_vigencia = data_atual.strftime("%d/%m/%Y %H:%M:%S")
    
            # Clica no botão 'Salvar'
            xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
            if self.browser.search_element(By.XPATH, xpath):
                self.browser.search_element(By.XPATH, xpath).click()
            else:  # Se o botão 'Salvar' não estiver ativo, clicar em 'Fechar'
                if not self.browser.element_click(By.XPATH, "//button[span[contains(text(), 'Fechar')]]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Fechar) não localizado."])
    
            # Verifica se salvou com sucesso
            xpath = f"//div[div[div[span[contains(text(),'{data_fim_vigencia}')]]]]"
            if self.browser.search_element(By.XPATH, xpath):
                return
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)
    
    
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
