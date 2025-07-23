from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA
from datetime import datetime, timedelta
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By, Keys


class EntradaUnicaPaciente(Tasy):

    def adicionar_atendimento(self, tipo_atendimento: str, clinica_atendimento: str, procedencia: str,
                              tipo_convenio: str, classificacao_atendimento: str, carater_atendimento: str = "",
                              tipo_acidente: str = "", tipo_atendimento_tiss: str = "", data_entrada: str = "",
                              cd_medico_atendente: str = "", observacao: str = "") -> str:
        """
        Adiciona um novo atendimento na função Entrada Única de Pacientes do Tasy.
        :return: Número do atendimento criado.
        """
        # Se a tela de atendimentos ainda não estiver no modo de edição, clica em 'Adicionar'
        if not self.bot.find_element("NR_ATENDIMENTO", By.NAME, waiting_time=1000, ensure_visible=True):
            # Clica em 'Adicionar'
            xpath = "//div[div[div[div[contains(text(),'Atendimentos')]]]]//*[contains(text(),'Adicionar')]"
            if not self.bot.element_click(xpath=xpath, tentativas=6):
                raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])
            # Clica em 'Atendimento'
            if not self.bot.element_click(xpath="//div[text()='Atendimento']", delay=1000, tentativas=4):
                raise Exception([LOG_EX_SISTEMA, "Botão (Atendimento) não localizado."])

        # Preenche o campo 'Tipo do atendimento'
        tipo_atendimento_atual = ""
        for n in range(3):
            self.bot.element_click(xpath="//div[input[@name='IE_TIPO_ATENDIMENTO']]", delay=1000, tentativas=4)
            self.bot.element_click(xpath=f"//a[span[text()='{tipo_atendimento}']]", delay=1000, tentativas=2)
            self.bot.tab()
            tipo_atendimento_atual = self.bot.element_get_text(xpath="//div[input[@name='IE_TIPO_ATENDIMENTO']]")
            if tipo_atendimento == tipo_atendimento_atual:
                break
            self.bot.wait(500)
        if tipo_atendimento != tipo_atendimento_atual:
            raise Exception([LOG_EX_SISTEMA, f"Tipo de atendimento ({tipo_atendimento}) não localizado."])

        # Pega o número do atendimento criado
        atendimento = self.bot.element_get_value(xpath="//input[@name='NR_ATENDIMENTO']", delay=1000)

        # Data da entrada
        if data_entrada:
            self.bot.find_element("DT_ENTRADA", By.NAME).click()
            self.bot.control_a()
            self.bot.find_element("DT_ENTRADA", By.NAME).send_keys(data_entrada)

        # Preenche o campo 'Clínica do atendimento'
        clinica_atendimento_atual = self.bot.search_element(xpath="//div[input[@name='IE_CLINICA'] and @tabindex='0']").text
        if clinica_atendimento_atual != clinica_atendimento:
            self.bot.search_element(xpath="//div[input[@name='IE_CLINICA'] and @tabindex='0']").click()
            if not self.bot.element_click(xpath=f"//a[span[text()='{clinica_atendimento}']]", delay=1000):
                raise Exception([LOG_EX_NEGOCIO, f"Clinica do atendimento ({clinica_atendimento}) não localizada."])

        # Preenche o campo 'Procedência'
        self.bot.element_click(xpath="//div[input[@name='CD_PROCEDENCIA']]")
        if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{procedencia}')]]", delay=1000):
            raise Exception([LOG_EX_NEGOCIO, f"Procedência ({procedencia}) não localizada."])

        # Preenche o campo 'Médico Atendente'
        self.bot.element_left_click(xpath="//input[@name='CD_MEDICO_RESP']") #  Clicando no campo para ele preenche automaticamente
        self.bot.tab()
        cd_medico_atendente_atual = ''
        for n in range(10):
            cd_medico_atendente_atual = self.bot.element_get_value(xpath="//input[@name='CD_MEDICO_RESP']")
            if cd_medico_atendente_atual != '':
                break
            self.bot.wait(500)
        if cd_medico_atendente and cd_medico_atendente != cd_medico_atendente_atual:
            # Se o médico nunca foi informado, aparece uma tela de pesquisa. Clicar em "Cancelar"
            if not cd_medico_atendente_atual:
                self.bot.element_click(xpath="//*[contains(text(), 'Cancelar')]")

            medico_anterior = self.bot.search_element(xpath="//div[div[*[div[div[input[@name='CD_MEDICO_RESP']]]]]]/div[2]/input").get_attribute("value")
            self.bot.search_element(xpath="//input[@name='CD_MEDICO_RESP']").send_keys(cd_medico_atendente)
            self.bot.tab()
            medico_novo = ''
            for n in range(10):
                medico_novo = self.bot.search_element(xpath="//div[div[*[div[div[input[@name='CD_MEDICO_RESP']]]]]]/div[2]/input").get_attribute("value")
                if medico_novo and medico_novo != medico_anterior:
                    break
                self.bot.wait(500)
            if not medico_novo or medico_novo == medico_anterior:
                raise Exception([LOG_EX_SISTEMA, f"Falha ao buscar o médito atendente."])

        elif not cd_medico_atendente_atual:
            raise Exception([LOG_EX_SISTEMA, "Médito atendente não localizado."])

        # Preenche o campo 'Tipo do convênio'
        tipo_convenio_atual = self.bot.element_get_text(xpath="//div[input[@name='IE_TIPO_CONVENIO']]")
        if tipo_convenio != tipo_convenio_atual:
            self.bot.element_click(xpath="//div[input[@name='IE_TIPO_CONVENIO']]")
            if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_convenio}']]", delay=1000):
                raise Exception([LOG_EX_NEGOCIO, f"Tipo do convênio ({tipo_convenio}) não localizado."])

        # Preenche o campo 'Caráter do atendimento'
        if carater_atendimento != "":
            self.bot.element_click(xpath="//div[input[@name='IE_CARATER_INTER_SUS']]")
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{carater_atendimento}')]]", delay=1000):
                raise Exception([LOG_EX_NEGOCIO, f"Caráter do atendimento ({carater_atendimento}) não localizado."])

        # Preenche o campo 'Tipo do acidente'
        if tipo_acidente != "":
            self.bot.element_click(xpath="//div[input[@name='NR_SEQ_TIPO_ACIDENTE']]")
            if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_acidente}']]", delay=1000):
                raise Exception([LOG_EX_NEGOCIO, f"Tipo do acidente ({tipo_acidente}) não localizado."])

        # Preenche o campo 'Classificação do atendimento'
        self.bot.element_click(xpath="//div[input[@name='NR_SEQ_CLASSIFICACAO']]")
        if not self.bot.element_click(xpath=f"//a[span[text()='{classificacao_atendimento}']]", delay=1000):
            raise Exception([LOG_EX_NEGOCIO, f"Classificação do atendimento ({classificacao_atendimento}) não localizada."])

        # Preenche o campo 'Tipo de atendimento TISS'
        if tipo_atendimento_tiss != "":
            self.bot.element_click(xpath="//div[input[@name='IE_TIPO_ATEND_TISS']]")
            if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_atendimento_tiss}']]", delay=1000):
                raise Exception([LOG_EX_NEGOCIO, f"Tipo de atendimento TISS ({tipo_atendimento_tiss}) não localizado."])

        # Preenche o campo 'Observação'
        if observacao != "":
            self.bot.search_element(xpath="//*[@name='DS_OBSERVACAO']").send_keys(observacao)

        # Clica no botão 'Salvar'
        if not self.bot.element_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception([LOG_EX_SISTEMA, f"Botão (Salvar) não localizado."])

        # Verificar se aparece o popup de 'Confirmação'
        if self.bot.search_element(xpath="//div[text()='Confirmação']", tentativas=3):
            self.bot.search_element(xpath="//*[contains(text(),'Cancelar')]").click()

        # Verificar se o atendimento criado aparece na tabela de atendimentos
        if self.bot.search_element(xpath=f"//span[text()='{atendimento}']", tentativas=20):
            return atendimento

        # Verificar se aparece o popup de 'Operação abortada'
        mensagem_erro = ''
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)

        raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
    def adicionar_convenio(self, convenio: str = '', categoria: str = '', tipo_acomodacao: str = '',
                           codigo_usuario: str = '', complemento: str = '', data_validade: str = '',
                           plano_produto: str = '', cobertura: str = '', tipo_guia: str = '', guia: str = '',
                           senha: str = '', data_inicio_vigencia: str = '', data_final_vigencia: str = '',
                           observacao: str = ''):
        """
        Adiciona ou atualizar dados do convênio na função Entrada Única de Pacientes no Tasy.
        :param convenio: Convênio
        :param categoria: Categoria do convênio;
        :param tipo_acomodacao: Tipo de acomodação;
        :param codigo_usuario: Carteirinha do paciente;
        :param complemento: Complemento da carteirinho;
        :param data_validade: Validade da carteirinha;
        :param plano_produto: Plano da carteirinha;
        :param cobertura: Cobertura do convênio;
        :param tipo_guia: Tipo de guia;
        :param guia: Guia da autorização;
        :param senha: Senha da autorização;
        :param data_inicio_vigencia: Data de início de vigência;
        :param data_final_vigencia: Data fim de vigência;
        :param observacao: Observação
        """
        # Se a tela do convênio ainda não estiver no modo de edição...
        if not self.bot.find_element("CD_USUARIO_CONVENIO", By.NAME, ensure_visible=True):
            # Se a aba "Setores" estiver ativa, é necessário clicar em "Cancelar", clicar em "Sair sem salvar"
            xpath = "//span[contains(text(), 'Setor de atendimento do paciente')]"
            if self.bot.search_element(xpath=xpath, tentativas=2):
                # Clicar em "Cancelar"
                self.bot.search_element(xpath="//*[*[*[*[contains(text(), 'Cancelar')]]]]").click()
                # No popup, clicar em "Sair sem salvar"
                self.bot.search_element(xpath="//*[contains(text(), 'Sair sem salvar')]").click()

            # Clicar na aba "Convênios"
            self.bot.search_element(xpath="//*[*[contains(text(), 'Convênios')]]").click()

            # Se a tela do convênio ainda não estiver no modo de edição, clica em 'Adicionar'
            if not self.bot.find_element("CD_USUARIO_CONVENIO", By.NAME, ensure_visible=True):
                xpath = "//div[div[div[div[contains(text(),'Convênio')]]]]//*[contains(text(),'Adicionar')]"
                if not self.bot.element_click(xpath=xpath):
                    raise Exception([LOG_EX_SISTEMA, f"Botão (Adicionar) não localizado."])

        # Preenche o campo 'Convênio'
        convenio_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CONVENIO']]//span", delay=1000)
        if convenio != "" and convenio != convenio_atual:
            self.bot.element_click(xpath="//div[input[@name='CD_CONVENIO']]", delay=1000)
            if not self.bot.element_click(xpath=f"//a[span[text()='{convenio}']]", delay=1000):
                raise Exception([LOG_EX_NEGOCIO, f"Convênio ({convenio}) não localizado."])

        # Preenche o campo 'Categoria'
        categoria_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CATEGORIA']]//span")
        if categoria != "" and categoria != categoria_atual:
            self.bot.element_click(xpath="//div[input[@name='CD_CATEGORIA']]", tentativas=4)
            if not self.bot.element_click(xpath=f"//a[span[text()='{categoria}']]", delay=1000, tentativas=4):
                raise Exception([LOG_EX_NEGOCIO, f"Categoria ({categoria}) não localizada."])

        # Preenche o campo 'Tipo de acomodação'
        tipo_acomodacao_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]//span")
        if tipo_acomodacao != "" and tipo_acomodacao != tipo_acomodacao_atual:
            self.bot.element_click(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]", tentativas=4)
            if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_acomodacao}']]", delay=1000, tentativas=4):
                raise Exception([LOG_EX_NEGOCIO, f"Tipo de acomodação ({tipo_acomodacao}) não localizada."])

        # Preenche o campo 'Código do usuário'
        codigo_usuario_atual = self.bot.element_get_value(xpath="//input[@name='CD_USUARIO_CONVENIO']")
        if codigo_usuario != "" and codigo_usuario != codigo_usuario_atual:
            self.bot.element_set_text(xpath="//input[@name='CD_USUARIO_CONVENIO']", text=codigo_usuario, tentativas=4)
            self.bot.tab()

        # Preenche o campo 'Complemento'
        complemento_atual = self.bot.element_get_value(xpath="//input[@name='CD_COMPLEMENTO']")
        if complemento != "" and complemento != complemento_atual:
            self.bot.element_set_text(xpath="//input[@name='CD_COMPLEMENTO']", text=complemento, tentativas=4)
            self.bot.tab()

        # Preenche o campo 'Data de validade'
        data_validade_atual = self.bot.element_get_value(xpath="//input[@name='DT_VALIDADE_CARTEIRA']")
        if data_validade != "" and data_validade != data_validade_atual:
            self.bot.element_set_text(xpath="//input[@name='DT_VALIDADE_CARTEIRA']", text=data_validade, tentativas=4)
            self.bot.tab()

        # Preenche o campo 'Plano/Produto'
        plano_produto_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_PLANO_CONVENIO']]//span")
        if plano_produto != "" and plano_produto != plano_produto_atual:
            self.bot.element_click(xpath="//div[input[@name='CD_PLANO_CONVENIO']]", tentativas=4)
            if not self.bot.element_click(xpath=f"//a[span[text()='{plano_produto}']]", delay=1000, tentativas=4):
                raise Exception([LOG_EX_NEGOCIO, f"Plano/Produto ({plano_produto}) não localizado."])

        # Preenche o campo 'Cobertura'
        cobertura_atual = self.bot.element_get_text(xpath="//div[input[@name='NR_SEQ_COBERTURA']]//span")
        if cobertura != "" and cobertura != cobertura_atual:
            self.bot.element_click(xpath="//div[input[@name='NR_SEQ_COBERTURA']]", tentativas=4)
            if not self.bot.element_click(xpath=f"//a[span[text()='{cobertura}']]", delay=1000, tentativas=4):
                raise Exception([LOG_EX_NEGOCIO, f"Cobertura ({cobertura}) não localizada."])

        # Preenche o campo 'Tipo da guia'
        tipo_guia_atual = self.bot.element_get_text(xpath="//div[input[@name='IE_TIPO_GUIA']]//span")
        if tipo_guia != "" and tipo_guia != tipo_guia_atual:
            self.bot.element_click(xpath="//div[input[@name='IE_TIPO_GUIA']]", tentativas=4)
            if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_guia}']]", delay=1000, tentativas=4):
                raise Exception([LOG_EX_NEGOCIO, f"Tipo de guia ({tipo_guia}) não localizada."])

        # Preenche o campo 'Guia'
        guia_atual = self.bot.element_get_value(xpath="//input[@name='NR_DOC_CONVENIO']")
        if guia != "" and guia != guia_atual:
            self.bot.element_set_text(xpath="//input[@name='NR_DOC_CONVENIO']", text=guia, tentativas=4)
            self.bot.tab()

        # Preenche o campo 'Senha'
        senha_atual = self.bot.element_get_value(xpath="//input[@name='CD_SENHA']")
        if senha != "" and senha != senha_atual:
            self.bot.element_set_text(xpath="//input[@name='CD_SENHA']", text=senha, tentativas=4)
            self.bot.tab()

        # Preenche o campo 'Data de início de vigência'
        data_inicio_vigencia_atual = self.bot.element_get_value(xpath="//input[@name='DT_INICIO_VIGENCIA']")
        if data_inicio_vigencia != "" and data_inicio_vigencia != data_inicio_vigencia_atual:
            self.bot.find_element(selector="//input[@name='DT_INICIO_VIGENCIA']", by=By.XPATH).click()
            self.bot.type_keys(keys=[Keys.CONTROL, "a"])
            self.bot.kb_type(data_inicio_vigencia)

        # Preenche o campo 'Data final da vigência'
        data_final_vigencia_atual = self.bot.element_get_value(xpath="//input[@name='DT_FINAL_VIGENCIA']")
        dt_final_vigencia_atual = datetime.now() - timedelta(days=1)
        if data_final_vigencia_atual:
            dt_final_vigencia_atual = datetime.strptime(data_final_vigencia_atual, "%d/%m/%Y %H:%M:%S")
        if data_final_vigencia or not data_final_vigencia_atual or dt_final_vigencia_atual <= datetime.now():
            if not data_final_vigencia:
                data_final_vigencia = (datetime.now() + timedelta(days=30)).strftime("%d%m%Y235959")
            self.bot.search_element(xpath="//input[@name='DT_FINAL_VIGENCIA']").clear()
            self.bot.search_element(xpath="//input[@name='DT_FINAL_VIGENCIA']").send_keys(data_final_vigencia)
            self.bot.tab()

        # Preenche o campo 'Observação'
        observacao_atual = self.bot.element_get_value(xpath="//*[@name='DS_OBSERVACAO']")
        if observacao != "" and observacao != observacao_atual:
            self.bot.element_set_text(xpath="//*[@name='DS_OBSERVACAO']", text=observacao, tentativas=4)
            self.bot.tab()

        # Verificar se aparece o popup de 'Operação abortada'
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        # Preenche o campo 'Categoria' novamente. O Tasy está limpando esse campo qualquer alteração
        categoria_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CATEGORIA']]//span")
        if categoria != "" and categoria != categoria_atual:
            self.bot.element_click(xpath="//div[input[@name='CD_CATEGORIA']]", tentativas=4)
            if not self.bot.element_click(xpath=f"//a[span[text()='{categoria}']]", delay=1000, tentativas=4):
                raise Exception([LOG_EX_NEGOCIO, f"Categoria ({categoria}) não localizada."])

        # Clica no botão 'Salvar'
        if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]", tentativas=4):
            raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])

        for n in range(4):
            # Se aparece um popup "Informação" ou "Confirmação", clica em 'Ok'
            xpath = "//*[text()='Informação' or contains(text(),'Confirmação')]"
            if self.bot.search_element(xpath=xpath, tentativas=2):
                self.bot.element_click(xpath="//*[contains(text(),'Ok')]")

        # Verificar se salvou com sucesso
        xpath = "//div[div[div[span[text()='Salvar']]] and contains(@class,'disable')]"
        if self.bot.search_element(xpath=xpath):
            # O botão de 'Salvar' ficar desabilitado é a única forma de verificar que salvou com sucesso.
            # Mesmo assim é necessário esperar um tempo a mais. Caso contrário o popup de confirmação aparece
            # self.bot.wait(5000)
            return

        # Verificar se aparece o popup de 'Operação abortada'
        mensagem_erro = ''
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)
            raise Exception([LOG_EX_NEGOCIO, mensagem_erro])

        raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
    def adicionar_setor(self, setor_atendimento_paciente: str, tipo_acomodacao: str = "", unidade_basica: str = ""):
        """
        Adiciona um setor na aba Setores da função Entrada Única de Pacientes do Tasy.
        :param setor_atendimento_paciente: Setor do atendimento do paciente;
        :param tipo_acomodacao: Tipo de acomodação;
        :param unidade_basica: Unidade básica.
        """
        # Se a tela do convênio ainda estiver ativa, clica na aba 'Setores'
        if self.bot.search_element(xpath="//div[contains(text(),'Convênio')]", tentativas=1):
            if not self.bot.element_click(xpath="//div[span[text()='Setores']]"):
                # Clica nos '...' que tem no canto superior esquerdo para exibir as opções de aba
                self.bot.find_element("elipsisButton", By.ID).click()
                # Clica em 'Setores'
                if not self.bot.element_click(xpath="//div[contains(text(),'Setores')]"):
                    raise Exception([LOG_EX_SISTEMA, "Aba (Setores) não localizada."])
                # Clica novamente nos '...' para ocultar o menu
                self.bot.find_element("elipsisButton", By.ID).click()

        # Se a tela de Setores não estiver no modo de edição, clica em 'Adicionar'
        if not self.bot.search_element(xpath="//div[input[@name='CD_SETOR_ATENDIMENTO']]"):
            xpath = "//div[div[div[div[contains(text(),'Setores')]]]]//*[contains(text(),'Adicionar')]"
            if not self.bot.element_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])

        # Preenche o campo 'Setor de atendimento do paciente'
        setor_atendimento_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_SETOR_ATENDIMENTO']]//span", delay=2000)
        if setor_atendimento_paciente != setor_atendimento_atual:
            self.bot.element_click(xpath="//div[input[@name='CD_SETOR_ATENDIMENTO']]", delay=1000)
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{setor_atendimento_paciente}')]]", delay=1000):
                raise Exception([LOG_EX_NEGOCIO, f"Setor ({setor_atendimento_paciente}) não localizado."])
            self.bot.tab()

            # Em alguns casos, aparece um popup 'Unidade Atendimento Disponível' para seleção da Unidade básica
            if self.bot.search_element(xpath="//span[text()='Unidade Atendimento Disponível']", tentativas=5):
                if not self.bot.element_click(xpath=f"//div[div[div[span[contains(text(),'{unidade_basica}')]]]]", delay=2000):
                    raise Exception([LOG_EX_NEGOCIO, f"Unidade básica ({unidade_basica}) não localizada."])
                self.bot.element_click(xpath=f"//button[span[contains(text(),'OK')]]")

            # Após selecionar o setor o tipo de acomodação e a Unidade básica são preenchidos automaticamente
            tipo_acomod_atual = ""
            for n in range(10):
                tipo_acomod_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]//span")
                if tipo_acomod_atual != "---":
                    break
                self.bot.wait(500)
            if tipo_acomod_atual == "---":
                raise Exception([LOG_EX_NEGOCIO, 'Tipo de acomodação não preenchido automaticamente.'])

        # Preenche o campo 'Tipo de acomodação'
        tipo_acomod_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]//span")
        if tipo_acomodacao != "" and tipo_acomodacao != tipo_acomod_atual:
            self.bot.element_click(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]")
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{tipo_acomodacao}')]]", delay=500):
                raise Exception([LOG_EX_NEGOCIO, f"Tipo de acomodação ({tipo_acomodacao}) não localizado."])

        # Clica no botão 'Salvar'
        if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])

        for n in range(5):
            # Se aparece um popup "Informação" ou "Confirmação", clica em 'Ok'
            xpath = "//*[text()='Informação' or contains(text(),'Confirmação')]"
            if self.bot.search_element(xpath=xpath, tentativas=5):
                self.bot.element_click(xpath="//*[contains(text(),'Ok')]")
                continue
            break

        # Verificar se salvou com sucesso
        xpath = "//div[div[span[contains(text(),'Setor')]] and div[span[text()='Básica']]]"
        if self.bot.search_element(xpath=xpath):
            return

        # Verificar se aparece o popup de 'Operação abortada'
        mensagem_erro = ''
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)

        raise Exception([LOG_EX_SISTEMA, mensagem_erro])    
    
    def gerar_alta_paciente(self, atendimento: str) -> None:
        """
        Clica com o botão direito na linha do atendimento, em seguida 'Atendimento -> Gerar alta paciente'.
        :param atendimento: Número do atendimento.
        """
        # Clica com o botão direito na linha do atendimento
        xpath = f"//div[div[div[span[text()='{atendimento}']]]]"
        if not self.bot.element_right_click(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, "Atendimento não localizado."])

        # Clica em 'Atendimento -> Gerar alta paciente'
        self.bot.element_click(xpath="//div[text()='Atendimento']")
        if not self.bot.element_click(xpath="//div[text()='Gerar alta paciente']"):
            raise Exception([LOG_EX_NEGOCIO, f"Menu (Gerar alta paciente) não localizado."])

        # Pega o atributo 'data-row-idx' da linha do atendimento
        data_row_idx = self.bot.find_element(selector=xpath, by=By.XPATH).get_attribute("data-row-idx")

        # Verificar se na coluna 'Status' aparece o simbolo da alta do paciente
        xpath = f"//div[@data-row-idx='{data_row_idx}']//div[contains(@onmouseenter,'Alta')]"
        if self.bot.search_element(xpath=xpath):
            return

        raise Exception([LOG_EX_SISTEMA, ""])
    
    def retornar_tabela_atendimentos(self) -> None:
        """
        Clica no botão 'Atendimento:' para retornar para a tela com a tabela de atendimentos.
        """
        # Retornar para a tela com a tabela de atendimentos
        if not self.bot.element_click(xpath="//div[div[text()='Atendimento']]", delay=1000):
            raise Exception([LOG_EX_SISTEMA, "Tela de atendimentos não localizada."])

        xpath = "//div[div[span[contains(text(),'Atendimento')]] and div[span[text()='Data da entrada']]]"
        if self.bot.search_element(xpath=xpath):
            return

        # Verificar se aparece o popup de 'Operação abortada'
        mensagem_erro = ''
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)

        raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
    def adicionar_diagnostico_medico(self, cid: str) -> None:
        """
        Adicionar novo diagnóstico médico na função Entrada Única de Pacientes do Tasy.
        :param cid: CID do paciente.
        """
        # Clica no menu central com o nome 'Dados do atendimento'
        if not self.bot.element_click(xpath="//div[a[*[span[text()='Dados do atendimento']]]]"):
            raise Exception([LOG_EX_SISTEMA, "Menu (Dados do atendimento) não localizado."])

        # Quando o menu de opções abrir, clica em 'Diagnóstico'
        if not self.bot.element_click(xpath="//a[span[text()='Diagnóstico']]", delay=500):
            raise Exception([LOG_EX_SISTEMA, "Menu (Diagnóstico) não localizado."])

        # Espera a tela de 'Diagnóstico médico' abrir
        if not self.bot.search_element(xpath="//div[contains(text(),'Diagnóstico médico')]"):
            raise Exception([LOG_EX_SISTEMA, "Tela de 'Diagnóstico médico' não localizada."])

        # Clica no botão 'Fechar'
        if not self.bot.element_click(xpath="//span[text()='Fechar']"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Fechar) não localizado."])

        # Clica no botão 'Adicionar' do lado esquerdo da tela (Diagnóstico médico)
        xpath = "//div[div[div[div[contains(text(),'Diagnóstico médico')]]]]//*[contains(text(),'Adicionar')]"
        if not self.bot.element_click(xpath=xpath, delay=500):
            raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])

        # Clica no campo 'Medico' para fazer o Tasy pesquisar o médico anterior
        self.bot.element_click(xpath="//input[@name='CD_MEDICO']")
        cd_medico_atual = ""
        for n in range(10):
            cd_medico_atual = self.bot.element_get_value(xpath="//input[@name='CD_MEDICO']", tentativas=1)
            if cd_medico_atual != "":
                break
            self.bot.wait(500)
        if cd_medico_atual == "":
            raise Exception(
                [LOG_EX_NEGOCIO, f"Médico não preenchido automaticamente pelo Tasy."])

        # Clica no botão 'Salvar'
        if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])

        # Verificar se salvou com sucesso
        mensagem_erro = ''
        xpath = "//div[div[span[contains(text(),'Medico')]] and div[span[text()='CRM']]]"
        if not self.bot.search_element(xpath=xpath):
            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro = self.bot.element_get_text(xpath=xpath)
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        # Clica no botão 'Adicionar' do lado direito da tela (Definição do diagnóstico)
        xpath = "//div[div[div[div[contains(text(),'Definição do diagnóstico')]]]]//*[contains(text(),'Adicionar')]"
        if not self.bot.element_click(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])

        # Preenche o campo 'CID 10'
        self.bot.element_set_text(xpath="//input[@name='CD_DOENCA']", text=cid)
        self.bot.tab()
        descricao_cid = ""
        for n in range(10):
            descricao_cid = self.bot.element_get_value(xpath="//input[@name='txDescription']")
            if descricao_cid != "":
                break
            self.bot.wait(500)
        if descricao_cid == "":
            raise Exception([LOG_EX_SISTEMA, f"CID ({cid}) não localizado."])

        # Clica no botão 'Salvar'
        if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])

        # Verificar se salvou com sucesso
        xpath = "//div[div[span[contains(text(),'CID 10')]] and div[span[text()='Doença']]]"
        if self.bot.search_element(xpath=xpath):
            return

        # Verificar se aparece o popup de 'Operação abortada'
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)

        raise Exception([LOG_EX_SISTEMA, mensagem_erro])
