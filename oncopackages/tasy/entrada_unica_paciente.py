from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By


class EntradaUnicaPaciente(Tasy):
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        super().__init__(bd_rpa, bd_tasy)

    def adicionar_atendimento(self,
                              tipo_atendimento: str,
                              clinica_atendimento: str,
                              procedencia: str,
                              tipo_convenio: str,
                              classificacao_atendimento: str,
                              carater_atendimento: str = "",
                              tipo_acidente: str = "",
                              tipo_atendimento_tiss: str = "") -> str:
        """
        Adiciona um novo atendimento na função Entrada Única de Pacientes do Tasy.
        :param tipo_atendimento: Tipo de atendimento;
        :param clinica_atendimento: Clínica do atendimento;
        :param procedencia: Procedência;
        :param tipo_convenio: Tipo de convênio;
        :param classificacao_atendimento: Classificação do atendimento;
        :param carater_atendimento: Caráter do atendimento;
        :param tipo_acidente: Tipo de acidente;
        :param tipo_atendimento_tiss: Tipo de atendimento TISS;
        :return: Número do atendimento criado.
        """
        mensagem_erro = "Falha ao adicionar um novo atendimento na Entrada Única de Pacientes. "
        try:
            # Se a tela de atendimentos ainda não estiver no modo de edição, clica em 'Adicionar'
            if not self.bot.find_element("NR_ATENDIMENTO", By.NAME, waiting_time=5000, ensure_visible=True):
                # Clica em 'Adicionar'
                xpath = "//div[div[div[div[contains(text(),'Atendimentos')]]]]//*[contains(text(),'Adicionar')]"
                if not self.bot.element_click(xpath=xpath, tentativas=6):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])
                # Clica em 'Atendimento'
                if not self.bot.element_click(xpath="//div[text()='Atendimento']", delay=250, tentativas=4):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Atendimento) não localizado."])

            # Pega o novo atendimento
            atendimento = ""
            for n in range(20):
                atendimento = self.bot.find_element("NR_ATENDIMENTO", By.NAME).get_attribute("value")
                if atendimento != "":
                    break
                self.bot.wait(500)
            if atendimento == "":
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Atendimento não gerado."])

            # Preenche o campo 'Tipo do atendimento'
            tipo_atendimento_atual = ""
            for n in range(3):
                self.bot.element_click(xpath="//div[input[@name='IE_TIPO_ATENDIMENTO']]", delay=1000, tentativas=4)
                self.bot.element_click(xpath=f"//a[span[text()='{tipo_atendimento}']]", delay=250, tentativas=2)
                self.bot.tab()
                tipo_atendimento_atual = self.bot.element_get_text(xpath="//div[input[@name='IE_TIPO_ATENDIMENTO']]")
                if tipo_atendimento == tipo_atendimento_atual:
                    break
                self.bot.wait(500)
            if tipo_atendimento != tipo_atendimento_atual:
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Tipo de atendimento ({tipo_atendimento}) não localizado."])

            # Preenche o campo 'Clínica do atendimento'
            self.bot.element_click(xpath="//div[input[@name='IE_CLINICA'] and @tabindex='0']")
            if not self.bot.element_click(xpath=f"//a[span[text()='{clinica_atendimento}']]", delay=250):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Clinica do atendimento ({clinica_atendimento}) não localizada."])

            # Preenche o campo 'Procedência'
            self.bot.element_click(xpath="//div[input[@name='CD_PROCEDENCIA']]")
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{procedencia}')]]", delay=250):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Procedência ({procedencia}) não localizada."])

            # Preenche o campo 'Médico Atendente'
            #   Clicando no campo ele preenche automaticamente
            cd_medico_atendente_atual = ''
            self.bot.element_left_click(xpath="//input[@name='CD_MEDICO_RESP']")
            for n in range(10):
                cd_medico_atendente_atual = self.bot.element_get_value(xpath="//input[@name='CD_MEDICO_RESP']")
                if cd_medico_atendente_atual != '':
                    break
                self.bot.wait(500)
            if cd_medico_atendente_atual == '':
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Médico Atendente não informado pelo Tasy."])

            # Preenche o campo 'Tipo do convênio'
            tipo_convenio_atual = self.bot.element_get_text(xpath="//div[input[@name='IE_TIPO_CONVENIO']]")
            if tipo_convenio != tipo_convenio_atual:
                self.bot.element_click(xpath="//div[input[@name='IE_TIPO_CONVENIO']]")
                if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_convenio}']]", delay=250):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Tipo do convênio ({tipo_convenio}) não localizado."])

            # Preenche o campo 'Caráter do atendimento'
            if carater_atendimento != "":
                self.bot.element_click(xpath="//div[input[@name='IE_CARATER_INTER_SUS']]")
                if not self.bot.element_click(xpath=f"//a[span[text()='{carater_atendimento}']]", delay=250):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Caráter do atendimento ({carater_atendimento}) não localizado."])

            # Preenche o campo 'Tipo do acidente'
            if tipo_acidente != "":
                self.bot.element_click(xpath="//div[input[@name='NR_SEQ_TIPO_ACIDENTE']]")
                if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_acidente}']]", delay=250):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Tipo do acidente ({tipo_acidente}) não localizado."])

            # Preenche o campo 'Classificação do atendimento'
            self.bot.element_click(xpath="//div[input[@name='NR_SEQ_CLASSIFICACAO']]")
            if not self.bot.element_click(xpath=f"//a[span[text()='{classificacao_atendimento}']]", delay=250):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Classificação do atendimento ({classificacao_atendimento}) não localizada."])

            # Preenche o campo 'Tipo de atendimento TISS'
            if tipo_atendimento_tiss != "":
                self.bot.element_click(xpath="//div[input[@name='IE_TIPO_ATEND_TISS']]")
                if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_atendimento_tiss}']]", delay=250):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Tipo de atendimento TISS ({tipo_atendimento_tiss}) não localizado."])

            # Clica no botão 'Salvar'
            if not self.bot.element_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Botão (Salvar) não localizado."])

            # Verificar se o atendimento criado aparece na tabela de atendimentos
            if self.bot.element_wait_displayed(xpath=f"//span[text()='{atendimento}']", tentativas=40):
                return atendimento

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def adicionar_convenio(self,
                           convenio: str = '',
                           categoria: str = '',
                           tipo_acomodacao: str = '',
                           codigo_usuario: str = '',
                           complemento: str = '',
                           data_validade: str = '',
                           plano_produto: str = '',
                           cobertura: str = '',
                           tipo_guia: str = '',
                           guia: str = '',
                           senha: str = '',
                           data_inicio_vigencia: str = '',
                           data_final_vigencia: str = '',
                           observacao: str = '') -> None:
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
        mensagem_erro = "Falha ao adicionar dados do convênio na Entrada Única de Pacientes. "
        try:
            # Se a tela do convênio ainda não estiver no modo de edição, clica em 'Adicionar'
            if not self.bot.find_element("CD_USUARIO_CONVENIO", By.NAME, waiting_time=5000, ensure_visible=True):
                xpath = "//div[div[div[div[contains(text(),'Convênio')]]]]//*[contains(text(),'Adicionar')]"
                if not self.bot.element_click(xpath=xpath):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Botão (Adicionar) não localizado."])

            # Preenche o campo 'Convênio'
            convenio_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CONVENIO']]//span")
            if convenio != "" and convenio != convenio_atual:
                self.bot.element_click(xpath="//div[input[@name='NR_SEQ_CLASSIFICACAO']]", tentativas=4)
                if not self.bot.element_click(xpath=f"//a[span[text()='{convenio}']]", delay=250, tentativas=4):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Convênio ({convenio}) não localizado."])

            # Preenche o campo 'Categoria'
            categoria_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_CATEGORIA']]//span")
            if categoria != "" and categoria != categoria_atual:
                self.bot.element_click(xpath="//div[input[@name='CD_CATEGORIA']]", tentativas=4)
                if not self.bot.element_click(xpath=f"//a[span[text()='{categoria}']]", delay=250, tentativas=4):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Categoria ({categoria}) não localizada."])

            # Preenche o campo 'Tipo de acomodação'
            tipo_acomodacao_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]//span")
            if tipo_acomodacao != "" and tipo_acomodacao != tipo_acomodacao_atual:
                self.bot.element_click(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]", tentativas=4)
                if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_acomodacao}']]", delay=250, tentativas=4):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Tipo de acomodação ({tipo_acomodacao}) não localizada."])

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
                if not self.bot.element_click(xpath=f"//a[span[text()='{plano_produto}']]", delay=250, tentativas=4):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Plano/Produto ({plano_produto}) não localizado."])

            # Preenche o campo 'Cobertura'
            cobertura_atual = self.bot.element_get_text(xpath="//div[input[@name='NR_SEQ_COBERTURA']]//span")
            if cobertura != "" and cobertura != cobertura_atual:
                self.bot.element_click(xpath="//div[input[@name='NR_SEQ_COBERTURA']]", tentativas=4)
                if not self.bot.element_click(xpath=f"//a[span[text()='{cobertura}']]", delay=250, tentativas=4):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Cobertura ({cobertura}) não localizada."])

            # Preenche o campo 'Tipo da guia'
            tipo_guia_atual = self.bot.element_get_text(xpath="//div[input[@name='IE_TIPO_GUIA']]//span")
            if tipo_guia != "" and tipo_guia != tipo_guia_atual:
                self.bot.element_click(xpath="//div[input[@name='IE_TIPO_GUIA']]", tentativas=4)
                if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_guia}']]", delay=250, tentativas=4):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Tipo de guia ({tipo_guia}) não localizada."])

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
                self.bot.element_set_text(xpath="//input[@name='DT_INICIO_VIGENCIA']", text=data_inicio_vigencia)
                self.bot.tab()

            # Preenche o campo 'Data final da vigência'
            data_final_vigencia_atual = self.bot.element_get_value(xpath="//input[@name='DT_FINAL_VIGENCIA']")
            if data_final_vigencia != "" and data_final_vigencia != data_final_vigencia_atual:
                self.bot.element_set_text(xpath="//input[@name='DT_FINAL_VIGENCIA']", text=data_final_vigencia)
                self.bot.tab()

            # Preenche o campo 'Observação'
            observacao_atual = self.bot.element_get_value(xpath="//*[@name='DS_OBSERVACAO']")
            if observacao != "" and observacao != observacao_atual:
                self.bot.element_set_text(xpath="//*[@name='DS_OBSERVACAO']", text=observacao, tentativas=4)
                self.bot.tab()

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])

            # Clica no botão 'Salvar'
            if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]", tentativas=4):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])

            # Verificar se salvou com sucesso
            xpath = "//div[div[div[span[text()='Salvar']]] and contains(@class,'disable')]"
            if self.bot.element_wait_displayed(xpath=xpath):
                # O botão de 'Salvar' ficar desabilitado é a única forma de verificar que salvou com sucesso.
                # Mesmo assim é necessário esperar um tempo a mais. Caso contrário o popup de confirmação aparece
                self.bot.wait(5000)
                return

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro])

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def adicionar_setores(self,
                          setor_atendimento_paciente: str,
                          tipo_acomodacao: str = "",
                          unidade_basica: str = "") -> None:
        """
        Adiciona um setor na aba Setores da função Entrada Única de Pacientes do Tasy.
        :param setor_atendimento_paciente: Setor do atendimento do paciente;
        :param tipo_acomodacao: Tipo de acomodação;
        :param unidade_basica: Unidade básica.
        """
        mensagem_erro = "Falha ao adicionar dados do setor na Entrada Única de Pacientes. "
        try:
            # Se a tela do convênio ainda estiver ativa, clica na aba 'Setores'
            if self.bot.element_wait_displayed(xpath="//div[contains(text(),'Convênio')]", tentativas=1):
                if not self.bot.element_click(xpath="//div[span[text()='Setores']]"):
                    # Clica nos '...' que tem no canto superior esquerdo para exibir as opções de aba
                    self.bot.find_element("elipsisButton", By.ID).click()
                    # Clica em 'Setores'
                    if not self.bot.element_click(xpath="//div[contains(text(),'Setores')]"):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Aba (Setores) não localizada."])
                    # Clica novamente nos '...' para ocultar o menu
                    self.bot.find_element("elipsisButton", By.ID).click()

            # Se a tela de Setores não estiver no modo de edição, clica em 'Adicionar'
            if not self.bot.element_wait_displayed(xpath="//div[input[@name='CD_SETOR_ATENDIMENTO']]", tentativas=6):
                xpath = "//div[div[div[div[contains(text(),'Setores')]]]]//*[contains(text(),'Adicionar')]"
                if not self.bot.element_click(xpath=xpath):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])

            # Preenche o campo 'Setor de atendimento do paciente'
            setor_atendimento_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_SETOR_ATENDIMENTO']]//span")
            if setor_atendimento_paciente != setor_atendimento_atual:
                self.bot.element_click(xpath="//div[input[@name='CD_SETOR_ATENDIMENTO']]")
                if not self.bot.element_click(xpath=f"//a[span[text()='{setor_atendimento_paciente}']]", delay=250):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Setor ({setor_atendimento_paciente}) não localizado."])
                self.bot.tab(2000)

                # Em alguns casos, aparece um popup 'Unidade Atendimento Disponível' para seleção da Unidade básica
                if self.bot.element_wait_displayed(xpath="//span[text()='Unidade Atendimento Disponível']", tentativas=4):
                    if not self.bot.element_click(xpath=f"//div[div[div[span[text()='{unidade_basica}']]]]", tentativas=2):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Unidade básica ({unidade_basica}) não localizada."])
                    self.bot.element_click(xpath=f"//button[span[contains(text(),'OK')]]")

                # Após selecionar o setor o tipo de acomodação e a Unidade básica são preenchidos automaticamente
                tipo_acomod_atual = ""
                for n in range(10):
                    tipo_acomod_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]//span")
                    if tipo_acomod_atual != "---":
                        break
                    self.bot.wait(500)
                if tipo_acomod_atual == "---":
                    raise Exception(['Excecao_Sistema', mensagem_erro + 'Tipo de acomodação não preenchido automaticamente.'])

            # Preenche o campo 'Tipo de acomodação'
            tipo_acomod_atual = self.bot.element_get_text(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]//span")
            if tipo_acomodacao != "" and tipo_acomodacao != tipo_acomod_atual:
                self.bot.element_click(xpath="//div[input[@name='CD_TIPO_ACOMODACAO']]")
                if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_acomodacao}']]", delay=250):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Tipo de acomodação ({tipo_acomodacao}) não localizado."])

            # Preenche o campo 'Unidade básica'
            unidade_basica_atual = self.bot.element_get_value(xpath="//input[@name='CD_UNIDADE_BASICA']")
            if unidade_basica != "" and unidade_basica != unidade_basica_atual:
                self.bot.element_set_text(xpath="//input[@name='CD_UNIDADE_BASICA']", text=unidade_basica)
                self.bot.tab()

            # Clica no botão 'Salvar'
            if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])

            # Verificar se salvou com sucesso
            xpath = "//div[div[span[contains(text(),'Setor')]] and div[span[text()='Básica']]]"
            if self.bot.element_wait_displayed(xpath=xpath):
                return

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def gerar_alta_paciente(self, atendimento: str) -> None:
        """
        Clica com o botão direito na linha do atendimento, em seguida 'Atendimento -> Gerar alta paciente'.
        :param atendimento: Número do atendimento.
        """
        mensagem_erro = "Falha ao gerar a alta do paciente na Entrada Única de Pacientes. "
        try:
            # Clica com o botão direito na linha do atendimento
            xpath = f"//div[div[div[span[text()='{atendimento}']]]]"
            if not self.bot.element_right_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Atendimento não localizado."])

            # Clica em 'Atendimento -> Gerar alta paciente'
            self.bot.element_click(xpath="//div[text()='Atendimento']")
            if not self.bot.element_click(xpath="//div[text()='Gerar alta paciente']"):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Menu (Gerar alta paciente) não localizado."])

            # Pega o atributo 'data-row-idx' da linha do atendimento
            data_row_idx = self.bot.find_element(selector=xpath, by=By.XPATH).get_attribute("data-row-idx")

            # Verificar se na coluna 'Status' aparece o simbolo da alta do paciente
            xpath = f"//div[@data-row-idx='{data_row_idx}']//div[contains(@onmouseenter,'Alta')]"
            if self.bot.element_wait_displayed(xpath=xpath):
                return

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def retornar_tabela_atendimentos(self) -> None:
        """
        Clica no botão 'Atendimento:' para retornar para a tela com a tabela de atendimentos.
        """
        mensagem_erro = "Falha ao retornar para a tela de Atendimentos na Entrada Única de Pacientes. "
        try:
            # Retornar para a tela com a tabela de atendimentos
            if not self.bot.element_click(xpath="//div[div[text()='Atendimento']]", delay=1000):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de atendimentos não localizada."])

            xpath = "//div[div[span[contains(text(),'Atendimento')]] and div[span[text()='Data da entrada']]]"
            if self.bot.element_wait_displayed(xpath=xpath):
                return

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def adicionar_diagnostico_medico(self, cid: str) -> None:
        """
        Adicionar novo diagnóstico médico na função Entrada Única de Pacientes do Tasy.
        :param cid: CID do paciente.
        """
        mensagem_erro = "Falha ao adicionar o diagnóstico médico na Entrada Única de Pacientes. "
        try:
            # Clica no menu central com o nome 'Dados do atendimento'
            if not self.bot.element_click(xpath="//div[a[*[span[text()='Dados do atendimento']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Menu (Dados do atendimento) não localizado."])

            # Quando o menu de opções abrir, clica em 'Diagnóstico'
            if not self.bot.element_click(xpath="//a[span[text()='Diagnóstico']]", delay=500):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Menu (Diagnóstico) não localizado."])

            # Espera a tela de 'Diagnóstico médico' abrir
            if not self.bot.element_wait_displayed(xpath="//div[contains(text(),'Diagnóstico médico')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de 'Diagnóstico médico' não localizada."])

            # Clica no botão 'Fechar'
            if not self.bot.element_click(xpath="//span[text()='Fechar']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Fechar) não localizado."])

            # Clica no botão 'Adicionar' do lado esquerdo da tela (Diagnóstico médico)
            xpath = "//div[div[div[div[contains(text(),'Diagnóstico médico')]]]]//*[contains(text(),'Adicionar')]"
            if not self.bot.element_click(xpath=xpath, delay=500):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])

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
                    [LOG_EX_NEGOCIO, mensagem_erro + f"Médico não preenchido automaticamente pelo Tasy."])

            # Clica no botão 'Salvar'
            if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])

            # Verificar se salvou com sucesso
            xpath = "//div[div[span[contains(text(),'Medico')]] and div[span[text()='CRM']]]"
            if not self.bot.element_wait_displayed(xpath=xpath):
                # Verificar se aparece o popup de 'Operação abortada'
                if self.bot.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                    xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                    mensagem_erro += self.bot.element_get_text(xpath=xpath)
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])

            # Clica no botão 'Adicionar' do lado direito da tela (Definição do diagnóstico)
            xpath = "//div[div[div[div[contains(text(),'Definição do diagnóstico')]]]]//*[contains(text(),'Adicionar')]"
            if not self.bot.element_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])

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
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"CID ({cid}) não localizado."])

            # Clica no botão 'Salvar'
            if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])

            # Verificar se salvou com sucesso
            xpath = "//div[div[span[contains(text(),'CID 10')]] and div[span[text()='Doença']]]"
            if self.bot.element_wait_displayed(xpath=xpath):
                return

            # Verificar se aparece o popup de 'Operação abortada'
            if self.bot.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.bot.element_get_text(xpath=xpath)

            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)
