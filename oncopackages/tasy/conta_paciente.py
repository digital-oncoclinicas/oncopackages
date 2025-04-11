from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By
import re


class ContaPaciente(Tasy):
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        super().__init__(bd_rpa, bd_tasy)

    def pesquisar_conta(self, nr_conta: str) -> None:
        """
        Função que realiza a pesquisa pelo número conta na função 'Conta Paciente' do Tasy.
        Args:
            nr_conta: Número da conta paciente a ser pesquisada.
        """
        mensagem_erro = "Falha ao pesquisar pela conta na função 'Conta Paciente'. "
        try:
            # Valida se a tela de filtro de pesquisa pela conta carregou corretamente
            xpath = f"//button[contains(text(),'Filtrar')]"
            if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True, ensure_clickable=True):
                try:
                    # Clicar no ícone de Filtro que fica no canto superior esquerdo
                    xpath = f"//tasy-wlabel[@uib-tooltip='Filtros em uso (Ctrl + Alt + F)'][@tooltip-append-to-body='true']"
                    self.bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).click()
                except:
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Filtro pesquisar conta não localizado."])

            # Verifica se o campo de pesquisa da conta paciente está disponível na tela
            if not self.bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo inserir o número da conta não localizado."])

            # Insere o Número da conta no campo de pesquisa
            xpath = "//input[@name='NR_INTERNO_CONTA']"
            if not self.bot.element_set_text(xpath=xpath, text=nr_conta, delay=1000):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo (Número da conta) não localizado."])

            # Clica no botão de 'filtro'
            xpath = f"//button[contains(text(),'Filtrar')]"
            self.bot.find_element(xpath, By.XPATH, ensure_visible=True, ensure_clickable=True).click()

            # Valida se a pesquisa retornou a conta
            xpath = f"//div[span[text()='{nr_conta}']]"
            if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Conta não foi localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def acessar_conta(self, conta: str) -> None:
        """
        Duplo click na linha referente a conta da função 'Conta Paciente' do Tasy.
        :param: conta: Conta que será acessada.
        """
        mensagem_erro = "Falha ao acessar a conta na função 'Conta Paciente'. "
        try:
            # Clica para ativar a linha da canta na tabela.
            xpath = f"//div[span[text()='{conta}']]"
            if not self.bot.element_click(xpath=xpath, delay=1000):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Conta ({conta}) não localizada."])

            # Duplo click para acessar a conta
            self.bot.element_double_click(xpath=xpath, delay=1000)

            # Valido carregamento da tela de detalhes da conta
            if not self.bot.search_element(xpath="//span[contains(text(), 'Procedimentos')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de detalhes da conta não localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def substituir_guia(self, conta: str, guia: str) -> None:
        """
        Acessa o menu clicando com o botão direito na linha da conta e seleciona a opção 'Substituir guia'.
        Args:
            conta: Número da conta paciente para validar carregamento da tela
            guia: Número da guia a ser substituído
        Returns: None
        """
        mensagem_erro = "Falha ao substituir a guia da conta. "
        try:
            # Click com o botão direito na primeira linha da tabela de contas
            if not self.bot.element_right_click(xpath=f"//div[span[text()='{conta}']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Conta não localizada."])

            # Clica na opção 'Substituir guia'
            if not self.bot.element_click(xpath="//div[text()='Substituir guia']", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Opção (substituir guia) não localizada."])

            # Aguarda a tela carregar
            if not self.bot.element_set_text(xpath="//input[@name='NR_NOVA_GUIA']", text=guia):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up (Substituir guia) não localizado."])

            # Clica em 'Ok'
            self.bot.element_click(xpath="//button[span[contains(text(),'OK')]]")

            # Valida se a guia foi substituída com sucesso
            for n in range(10):  # Verificar se a guia aparece na tabela
                if not self.bot.search_element(xpath=f"//span[text()='Substituir guia']", tentativas=1):
                    return
                self.bot.wait(500)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível validar a substituição."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def substituir_senha(self, conta: str, senha: str, substituir_todas: bool = False) -> None:
        """
        Acessa o menu clicando com o botão direito na linha da conta e seleciona a opção 'Substituir senha'.
        Args:
            conta: Número da conta paciente para validação de carregamento da tela
            senha: Nova Senha a ser substituída
            substituir_todas: Flegar o checkbox 'Substituir todas'?
        Returns: None
        """
        mensagem_erro = "Falha ao substituir a senha da conta. "
        try:
            # Click com o botão direito na linha da conta
            if not self.bot.element_right_click(xpath=f"//div[span[text()='{conta}']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Conta não localizada."])

            # Clica na opção 'Substituir senha'
            if not self.bot.element_click(xpath="//div[text()='Substituir senha']", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Opção (Substituir senha) não localizada."])

            # Aguarda pop-up 'Substituir senha' carregar
            if not self.bot.search_element(xpath="//input[@name='DS_NOVA_SENHA']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up (Substituir senha) não localizado."])

            # Flega o check-box 'Substituir todas'
            if substituir_todas:
                if not self.bot.element_click(xpath="//div[input[@name='IE_SUBSTITUIR']]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Checkbox (Substituir todas) não localizado."])
            else:
                # Insere a Senha
                self.bot.element_set_text(xpath="//input[@name='DS_SENHA']", text=senha)
                self.bot.tab()

            # Insere a Nova Senha
            self.bot.element_set_text(xpath="//input[@name='DS_NOVA_SENHA']", text=senha)
            self.bot.tab()

            # Clica em 'Ok'
            if not self.bot.element_click(xpath="//button[span[contains(text(),'OK')]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            # Valida se a senha foi substituída com sucesso
            for n in range(10):  # Verificar se a senha aparece na tabela
                if not self.bot.search_element(xpath=f"//span[text()='Substituir senha']", tentativas=1):
                    return
                self.bot.wait(500)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível validar a substituição."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def recalcular_conta(self, conta: str) -> None:
        """
        Acessa o menu clicando com o botão direito na linha da conta, e seleciona a opção recalcular conta.
        Args:
            conta: Número da conta paciente
        Returns: None
        """
        mensagem_erro = "Falha ao recalcular a conta do paciente. "
        try:
            # Click com o botão direito na linha da conta
            if not self.bot.element_right_click(xpath=f"//div[span[text()='{conta}']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Conta não localizada."])

            # Clicar em 'Recalcular conta'
            if not self.bot.element_click(xpath="//div[text()='Recalcular conta']", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Opção (Recalcular conta) não localizada."])

            # Aguardar o pop-up de confirmação
            xpath = "//div[text()='Conta atualizada com sucesso!']"
            if not self.bot.find_element(xpath, By.XPATH, 15000, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up de confirmação não localizado."])

            # Clica em 'Ok'
            if not self.bot.element_click(xpath="//button[span[contains(text(),'OK')]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            # Valida se retornou para a tela inicial
            for n in range(10):
                if not self.bot.search_element(xpath="//div[text()='Conta atualizada com sucesso!']", tentativas=1):
                    return
                self.bot.wait(500)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível validar a atualização."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def atualizar_conta_tiss(self, conta: str) -> None:
        """
        Acessa o menu clicando com o botão direito na linha da conta e seleciona a opção 'Atualizar conta TISS'.
        Args:
            conta: Número da conta paciente para validação de carregamento da tela
        Returns: None
        """
        mensagem_erro = "Falha ao atualizar a conta TISS. "
        try:
            # Click com o botão direito na linha da conta
            if not self.bot.element_right_click(xpath=f"//div[span[text()='{conta}']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Conta não localizada."])

            # Clica na opção 'Atualizar conta TISS'
            if not self.bot.element_click(xpath="//div[text()='Atualizar conta TISS']", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Opção (Atualizar conta TISS) não localizada."])

            # Aguarda pop-up de confirmação
            if not self.bot.search_element(xpath="//div[text()='Conta atualizada com sucesso!']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up de confirmação não localizado."])

            # Clica em 'Ok'
            if not self.bot.element_click(xpath="//button[text()='Ok']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            # Valida se retornou para a tela inicial
            for n in range(10):
                if not self.bot.search_element(xpath="//div[text()='Conta atualizada com sucesso!']", tentativas=1):
                    return
                self.bot.wait(500)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível validar a atualização."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def fechar_atendimento(self, conta: str) -> None:
        """
        Clica com o botão direito na linha da conta, seleciona a opção fechar atendimento e verifica se há inconsistência.
        Args:
            conta: Número da conta paciente para validação de carregamento da tela
        Returns: None
        """
        mensagem_erro = "Falha ao mudar status da conta. "
        try:
            # Click com o botão direito na linha da conta
            if not self.bot.element_right_click(xpath=f"//div[span[text()='{conta}']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Conta não localizada."])

            # Clica na opção 'Fechar atendimento'
            if not self.bot.element_click(xpath="//div[text()='Fechar atendimento']", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Opção (Fechar atendimento) não localizada."])

            # Aguardar o pop-up de confirmação
            xpath = fr"//div[text()='Confirma o final do atendimento?']"
            if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, "Pop-up de confirmação não localizado."])

            # Clica em 'Ok'
            if not self.bot.element_click(xpath="//button[text()='Ok']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            # Aguardar o popup de 'Consistência' (demora bastante)
            xpath = fr"//div[@title='Consistência']"
            if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True, waiting_time=60000):
                raise Exception([LOG_EX_SISTEMA, "Popup (Consistência) não localizada."])

            # Verificar se possuí alguma inconsistência na tabela de Consistências
            inconsistencia = self.bot.verificar_tabela_consistencia()
            if inconsistencia:
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + inconsistencia])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def mudar_status_conta(self, conta) -> None:
        """
        Clica com o botão direito na linha da conta e seleciona a opção 'Muda status conta'.
        Args:
            conta: Número da conta paciente para validação de carregamento da tela
        Returns: None
        """
        mensagem_erro = "Falha ao mudar o status da conta. "
        try:
            # Click com o botão direito na linha da conta
            if not self.bot.element_right_click(xpath=f"//div[span[text()='{conta}']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Conta não localizada."])

            # Clica na opção 'Muda status conta'
            if not self.bot.element_click(xpath="//div[text()='Muda status conta']", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Opção (Muda status conta) não localizada."])

            # Verificar se aparece o pop-up de inconsistência
            if self.bot.search_element(xpath="//div[contains(text(),'Inconsistências')]", tentativas=6):
                raise Exception([LOG_EX_NEGOCIO, "Popup (Inconsistências) encontrado."])

            # Aguardar o popup de 'Consistência' (demora bastante)
            xpath = "//div[@title='Consistência']"
            if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True, waiting_time=60000):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Popup (Consistência) não localizada."])

            # Verificar se possuí alguma inconsistência na tabela de Consistências
            incosistencia = self.bot.verificar_tabela_consistencia()

            # Clica em 'Ok'
            xpath = "//div[@class='region-cel' and //div[@title='Consistência']]//button[span[text()='OK']]"
            if not self.bot.element_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            if incosistencia:
                # Duplo click na linha referente a conta
                self.bot.acessar_conta(conta=conta)

                # Adicionar etapa na conta
                self.bot.adicionar_etapa(etapa="RPA", observacoes=incosistencia)

                # Reportar exceção de negócio
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + incosistencia])

            # Valida se retornou para a tela inicial
            for n in range(10):
                if not self.bot.search_element(xpath="//div[@title='Consistência']", tentativas=1):
                    return
                self.bot.wait(500)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível validar a mudança."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def inserir_conta_protocolo(self, identificador_protocolo: str) -> None:
        """
        Função insere a conta em um protocolo
        Args:
            identificador_protocolo: Identificador do protocolo a ser atribuído a conta
        Returns: None
        """
        mensagem_erro = "Falha ao inserir a conta no protocolo. "
        try:
            # Aguarda o carregamento do pop-up de inserir no protocolo
            if not self.bot.search_element(xpath="//span[text()='Inserir no protocolo']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up (Inserir no protocolo) não localizado."])

            # Preencher o campo 'Nome'
            self.bot.element_click(xpath="//div[input[@name='NR_PROTOCOLO']]", delay=1000)
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{identificador_protocolo}')]]", delay=250):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Protocolo não localizado."])

            # Clica em 'Ok'
            if not self.bot.element_click(xpath="//button[span[contains(text(),'OK')]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            # Após clicar em 'Ok', aparece um segundo popup de confirmação. Clica em 'Ok' novamente
            if not self.bot.element_click(xpath="//button[text()='Ok']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up de Confirmação não foi localizado."])

            # A conta foi inserida com sucesso se aparecer o popup 'Atenção' com a quantidade de contas no protocolo
            if self.bot.search_element(xpath="//div[text()='Atenção']"):
                # Clica em 'Ok'
                self.bot.element_click(xpath="//button[text()='Ok']")
                return

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=4):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def verificar_tabela_consistencia(self) -> str:
        """
        Função faz um loop pela tabela de consistência para verificar se possuí alguma inconsistência.
        Returns: Inconsistência encontrada
        """
        mensagem_erro = "Falha ao verificar tabela de consistências. "
        try:
            # Pega a quantidade de linhas na tabela de consistências
            xpath = "//div[div[div[div[div[span[text()='Consistência']]]]]]//i[@id='totalRecordsPageFinish']"
            qt_registros = self.bot.element_get_text(xpath=xpath)
            qt_registros = int(re.sub(r"[^0-9]", "", qt_registros)) + 1

            # Xpath tabela
            xpath_tabela = "//div[contains(@ng-repeat,'rowContainer')]"

            # Loop pela tabela de Consistências do tasy
            for num_linha in range(1, qt_registros):

                # 5 = Coluna 'FC'
                num_coluna = 5

                # Pega o valor da coluna 'FC'
                xpath = f"({xpath_tabela})[{num_linha}]/div/div/div[{num_coluna}]"
                fc = self.bot.find_element(xpath, By.XPATH, ensure_visible=True).text

                # Reportar o erro se o valor da coluna 'FC' for diferente de 'Sim'
                if fc != 'Sim':
                    #  2 = Coluna 'Inconsistência'
                    num_coluna = 2

                    # Pega o valor da coluna 'Inconsistência'
                    xpath = f"({xpath_tabela})[{num_linha}]/div/div/div[{num_coluna}]"
                    inconsistencia = self.bot.find_element(xpath, By.XPATH, ensure_visible=True).text

                    # Reportar a inconsistência
                    return inconsistencia

            return ""

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def adicionar_etapa(self, etapa: str, observacoes: str) -> None:
        """
        Adiciona uma nova etapa á conta.
        Args:
            etapa: Nome da etapa a ser inserida
            observacoes: Mensagem á ser adiciona no campo 'Observações'.
        Returns: None
        """
        mensagem_erro = "Falha ao adicionar etapa na conta do paciente. "
        try:
            # Clica na aba 'Etapa conta'
            if not self.bot.element_click(xpath="//div[span[text()='Etapas conta']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Menu (Etapas conta) não localizado."])

            # Clica no botão 'Adicionar'
            if not self.bot.element_click(xpath="//*[span[text()='Adicionar']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não foi localizado."])

            # Preenche o campo 'Etapa'
            self.bot.element_click(xpath="//div[input[@name='NR_SEQ_ETAPA']]")
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{etapa}')]]", delay=250):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Etapa ({etapa}) não localizada."])

            # Preenche o campo 'Observações'
            self.bot.element_set_text(xpath="//*[@name='DS_OBSERVACAO']", text=observacoes)
            self.bot.tab()

            # Clica no botão 'Salvar'
            if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])

            # Verificar se salvou com sucesso
            xpath = "//div[div[span[contains(text(),'Setor')]] and div[span[text()='Básica']]]"
            if self.bot.search_element(xpath=xpath):
                return

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def adicionar_conta(self, convenio: str, categoria: str = '', categoria_calculo: str = '') -> str:
        """
        Adiciona uma nova conta na função 'Conta Paciente' do Tasy.
        :param convenio:
        :param categoria:
        :param categoria_calculo:
        :return: Número da conta criada.
        """
        mensagem_erro = "Falha ao adicionar uma nova conta na função Conta Paciente. "
        try:
            # Clica em 'Adicionar'
            if not self.bot.element_click(xpath="//*[contains(text(),'Adicionar')]", delay=1000):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Botão (Adicionar) não localizado."])

            # Pega a nova conta
            conta = self.bot.element_get_value(xpath="//input[@name='NR_INTERNO_CONTA']")
            # conta = ""
            # for n in range(20):
            #     conta = self.bot.element_get_value(xpath="//input[@name='NR_INTERNO_CONTA']")
            #     if conta != "":
            #         break
            #     bot.wait(500)
            # if conta == "":
            #     raise Exception([LOG_EX_SISTEMA, error_manager + "Conta não gerada."])

            # Preenche o campo 'Convênio'
            convenio_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CONVENIO_PARAMETRO']]")
            if convenio != convenio_atual:
                self.bot.element_click(xpath="//div[input[@name='CD_CONVENIO_PARAMETRO']]")
                if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{convenio}')]]", delay=250):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Convênio ({convenio}) não localizado."])

            # Preenche o campo 'Categoria'
            categoria_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CATEGORIA_PARAMETRO']]")
            if categoria != "" and categoria != categoria_atual:
                self.bot.element_click(xpath="//div[input[@name='CD_CATEGORIA_PARAMETRO']]")
                if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{categoria}')]]", delay=250):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Categoria ({categoria}) não localizada."])

            # Preenche o campo 'Categoria cálculo'
            categoria_calculo_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CATEGORIA_CALCULO']]")
            if categoria_calculo != "" and categoria_calculo != categoria_calculo_atual:
                self.bot.element_click(xpath="//div[input[@name='CD_CATEGORIA_CALCULO']]")
                if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{categoria_calculo}')]]", delay=250):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Categoria cálculo ({categoria_calculo}) não localizada."])

            # Clica no botão 'Salvar'
            if not self.bot.element_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])

            # Verificar se a conta criada aparece na tabela de contas
            if self.bot.search_element(xpath=f"//span[text()='{conta}']", tentativas=20):
                return conta

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def adicionar_taxa(self,
                       procedimento: str,
                       quantidade: str,
                       motivo_inclusao: str,
                       data_procedimento: str = None) -> None:
        """
        Adicionar uma nova taxa na conta do paciente.
        :param: conta: Conta do paciente.
        """
        mensagem_erro = "Falha ao adicionar taxa na conta. "
        try:
            # Acessar a aba 'Taxa'
            if not self.bot.element_click(xpath="//div[span[text()='Taxa']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Aba (Taxa) não localizada."])

            # Clica em 'Adicionar'
            if not self.bot.element_click(xpath="//*[contains(text(),'Adicionar')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])

            # Pega a sequência da taxa
            sequencia = self.bot.element_get_value(xpath="//input[@name='NR_SEQUENCIA']")
            # bot.wait(1000)

            # Preenche o campo 'Procedimento'
            self.bot.element_set_text(xpath="//input[@name='NR_SEQ_PROC_INTERNO']", text=procedimento, delay=1000)
            cd_procedimento = ""
            for n in range(10):
                cd_procedimento = self.bot.element_get_value(xpath="//input[@name='CD_PROCEDIMENTO']", tentativas=1)
                if cd_procedimento != "":
                    break
                if self.bot.search_element(xpath="//div[contains(text(),'Informação')]", tentativas=2):
                    xpath = "//div[div[div[div[contains(text(),'Informação')]]]]/div[2]/div"
                    mensagem_erro += self.bot.element_get_text(xpath=xpath)
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro])
                self.bot.wait(500)
            if cd_procedimento == "":
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Procedimento não localizado."])

            # Preenche o campo 'Quantidade'
            self.bot.element_set_text(xpath="//input[@name='QT_PROCEDIMENTO']", text=quantidade)
            self.bot.tab()

            # Preenche o campo 'Data procedimento'
            if data_procedimento:
                self.bot.element_set_text(xpath="//input[@name='DT_PROCEDIMENTO']", text=data_procedimento)
                self.bot.tab()

            # Clica no botão 'Salvar'
            if not self.bot.element_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])

            # No popup que aparece preenche o 'Motivo de inclusão'
            self.bot.element_click(xpath="//div[input[@name='NR_SEQ_MOTIVO_INCL']]", delay=1000)
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{motivo_inclusao}')]]", delay=250):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Motivo de inclusão ({motivo_inclusao}) não localizado."])

            # Clica no botão 'Ok'
            if not self.bot.element_click(xpath="//button[span[contains(text(),'OK')]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            # Verifica se o pop-up de 'Consistência' aparece
            xpath = "//div[@title='Consistência']"
            if self.bot.find_element(xpath, By.XPATH, ensure_visible=True, waiting_time=3000):
                inconsistencia = self.bot.verificar_tabela_consistencia()
                if inconsistencia:
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + inconsistencia])
                # Clica em 'Ok'
                if not self.bot.element_click(xpath="//button[span[contains(text(),'OK')]]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])

            # Verificar se a taxa criada aparece na tabela de taxas
            # if self.bot.search_element(xpath=f"//div[span[text()='{sequencia}']]"):
            #     return
            if self.bot.bd_tasy.confirmar_taxa_adicionada(nr_sequencia=sequencia):
                # Às vezes aparece um pop-up de "Informação". Clica em 'Ok'
                if self.bot.search_element(xpath="//div[contains(text(),'Informação')]", tentativas=4):
                    if not self.bot.element_click(xpath="//button[contains(text(),'Ok')]"):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])
                return

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def retornar_tela_contas(self) -> None:
        """
        Retornar para a tela de contas clicando no nome 'Conta:' que fica no canto superior esquerdo da tela.
        """
        mensagem_erro = "Falha ao retornar para a tela de contas. "
        try:
            # Clica para ativar a linha da canta na tabela.
            self.bot.element_click(xpath="//div[div[text()='Conta']]", tentativas=4)

            # Valido carregamento da tela de detalhes da conta
            if not self.bot.search_element(xpath="//div[contains(text(),'Contas')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de contas não localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def anexar_arquivo_conta(self, dir_arquivo: str) -> None:
        """
        Realiza o upload do arquivo na aba Anexo da conta.
        """
        mensagem_erro = "Falha ao anexas arquivo na conta. "
        try:
            # Clica para ativar a linha da canta na tabela.
            self.bot.element_click(xpath="//div[div[text()='Conta']]", tentativas=4)

            # Valido carregamento da tela de detalhes da conta
            if not self.bot.search_element(xpath="//div[contains(text(),'Contas')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de contas não localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)
