from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By, Keys
import re


class ProtocoloConvenio(Tasy):
    def __init__(self, bd_rpa, bd_tasy=None):
        super().__init__(bd_rpa, bd_tasy)
    
    def pesquisar_sequencia_protocolo(self, seq_protocolo: str) -> None:
        """
        Realiza a pesquisa pela sequência do protocolo na função Protocolo Convênio do Tasy.
        Args:
             seq_protocolo: str: Sequência do protocolo.
        """
        mensagem_erro = "Falha ao pesquisar pela sequência do protocolo na função Protocolo Convênio. "
        try:
            # Verifica se a tela de filtros esta na tela
            if not self.element_wait_displayed(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=20):
                # Clicar no ícone de Filtro que fica no canto superior esquerdo
                self.element_click(xpath="//*[contains(@class,'filter-icon')]")
    
                # Espera a tela carregar
                if not self.element_wait_displayed(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=20):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de pesquisa não localizada."])
    
            # Preencher o campo 'Sequência protocolo'
            if not self.element_set_text(xpath="//input[@name='NR_SEQ_PROTOCOLO']", text=seq_protocolo, delay=1000):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Campo (Sequência protocolo) não localizado."])
            self.tab()
    
            # Clica no botão Filtrar
            if not self.element_click(xpath="//button[contains(text(), 'Filtrar')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Botão (Filtrar) não localizado."])
    
            # Aguarda a tela carregar
            if self.element_wait_displayed(xpath=f"//div[span='{seq_protocolo}']"):
                return
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def pesquisar_convenio(self, convenio: str) -> None:
        """
        Função pesquisa pelos protocolos associados ao convênio.
        Args:
            convenio: Nome do convênio filtrado
        Returns: None
    
        """
        mensagem_erro = "Falha ao pesquisar pelo convênio na função Protocolo Convênio. "
        try:
            # Verifica se a tela de filtros já está aberta
            if not self.element_wait_displayed(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=10):
                # Clicar no ícone de Filtro que fica no canto superior esquerdo
                self.element_click(xpath="//*[contains(@class,'filter-icon')]")
    
                # Espera a tela carregar
                if not self.element_wait_displayed(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=10):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de pesquisa não localizado."])
    
            # Preencher o campo 'Convênio'
            self.element_click(xpath="//div[input[@name='CD_CONVENIO']]", delay=500)
            if not self.element_click(xpath=f"//a[span[text()='{convenio}']]", delay=250):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Convênio ({convenio}) não localizado."])
    
            # Clica no botão Filtrar
            self.element_click(xpath="//button[contains(text(), 'Filtrar')]")
    
            # Aguarda a tela carregar
            if self.element_wait_displayed(xpath="//*[contains(text(),'Adicionar')]", tentativas=30):
                return
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def acessar_protocolo(self, seq_protocolo: str) -> None:
        """
        Realiza a pesquisa pela sequência do protocolo na função Protocolo Convênio do Tasy.
        Args:
             seq_protocolo: str: sequência do protocolo.
        """
        mensagem_erro = "Falha ao acessar o protocolo. "
        try:
            # Duplo click na linha do protocolo
            self.element_double_click(xpath=f"//div[span='{seq_protocolo}']")
    
            if not self.find_element("//span[contains(text(), 'Procedimentos')]", By.XPATH, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de detalhes do procolo não localizada."])
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def alterar_documento_convenio(self, protocolo: str, desc_doc_convenio: str) -> None:
        """
        Função altera o campo de Documento Convênio
        Args:
            protocolo: Sequencia do protocolo
            desc_doc_convenio: Conteúdo a ser adicionado ou substituído no campo
        """
        mensagem_erro = "Falha ao alterar o documento convênio. "
        try:
            # Clica com o botão direito do mouse na linha do protocolo
            if not self.element_right_click(xpath=f"//div[span='{protocolo}']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Protocolo não localizada."])
    
            # Click na opção "Alterar"
            self.find_element("(//div[contains(text(), 'Alterar')])[2]", By.XPATH).click()
    
            # Click na opção de alterar o Documento Convenio
            self.find_element("//div[contains(text(), 'Alterar o documento do convênio')]", By.XPATH).click()
    
            # Aguarda o pop-up abrir
            if not self.find_element("//span[contains(text(),'Alterar doc. convênio')]", By.XPATH):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up para altera doc convenio não foi localizado."])
            self.wait(1000)
    
            # Insere a sequência do Protocolo no campo
            xpath = "//input[@name='NR_SEQ_DOC_CONV']"
            self.find_element(xpath, By.XPATH, ensure_clickable=True).clear()
            self.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(desc_doc_convenio)
    
            # Clica em" OK "
            self.find_element("//button[span[contains(text(),'OK')]]", By.XPATH).click()
    
            # Valida a alteração do documento convênio
            xpath = fr"//div[span[text()='{desc_doc_convenio}']]"
            if not self.find_element(xpath, By.XPATH, ensure_visible=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Alteração doc. convênio não localizada."])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def adicionar_protocolo(self,
                            tipo_protocolo: str,
                            data_referencia: str,
                            identificacao_protocolo: str,
                            periodo_inicial_conta: str,
                            periodo_final_conta: str) -> str:
        """
        Adicionar um novo protocolo na função Protocolo Convênio do Tasy
        Args:
            tipo_protocolo: tipo do protocolo (ex.: SADT/Consulta)
            data_referencia: Valor do campo 'Data referência' no formato 'DD/MM/YYYY'
            identificacao_protocolo: Texto que será concatenado com a sequência e inserido no campo
            'Identificação do protocolo'. (max. 37 caracteres)
            periodo_inicial_conta: Valor do campo 'Período inicial conta' no formato DD/MM/YYYY HH:MM:SS
            periodo_final_conta:  Valor do campo 'Período final conta' no formato DD/MM/YYYY 23:59:59
    
        Returns: Sequência do protocolo
        """
        mensagem_erro = "Falha ao criar um novo protocolo. "
        try:
            # Clica no botão adicionar para criar um protocolo
            if not self.element_click(xpath="//*[span[contains(text(),'Adicionar')]]", delay=1000):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])
    
            # Pega o número do campo 'Sequência'
            protocolo = self.element_get_value(xpath="//input[@name='NR_SEQ_PROTOCOLO']", delay=1000)
    
            # Preencher o campo 'Tipo protocolo'
            self.element_click(xpath="//div[input[@name='IE_TIPO_PROTOCOLO']]")
            if not self.element_click(xpath=f"//a[span[text()='{tipo_protocolo}']]", delay=250):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Tipo protocolo ({tipo_protocolo}) não localizado."])
    
            # Preenche o campo 'Data referência'
            self.element_set_text(xpath="//input[@name='DT_MESANO_REFERENCIA']", text=data_referencia)
    
            # Preencher o campo 'Identificação protocolo'
            identificacao_protocolo = f"{protocolo}_{identificacao_protocolo}"
            self.element_set_text(xpath="//input[@name='NR_PROTOCOLO']", text=identificacao_protocolo)
    
            # Preenche o campo 'Período inicial conta'
            self.element_set_text(xpath="//input[@name='DT_PERIODO_INICIAL']", text=periodo_inicial_conta)
    
            # Preenche o campo 'Período final conta'
            self.element_set_text(xpath="//input[@name='DT_PERIODO_FINAL']", text=periodo_final_conta)
    
            # Clica no botão 'Salvar'
            if not self.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])
    
            # Verificar se salvou com sucesso
            if self.element_wait_displayed(xpath=f"//span[text()='{protocolo}']", tentativas=40):
                return protocolo
    
            # Verificar se aparece o popup de 'Operação abortada'
            if self.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.element_get_text(xpath=xpath)
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def mudar_status_protocolo(self, protocolo: str) -> None:
        """
        Função muda o status do protocolo para "Definitivo"
        Args:
            protocolo: Sequência do protocolo
        Returns: None
        """
        mensagem_erro = "Falha ao mudar status do protocolo. "
        try:
            # Clica com o botão direito do mouse na linha do protocolo
            if not self.element_right_click(xpath=f"//div[span='{protocolo}']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Protocolo não localizada."])
    
            # Click na opção "Mudar status"
            if not self.element_click(xpath="//div[text()='Muda status']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Menu (Mudar status) não localizado."])
    
            # Verificar se salvou com sucesso
            if self.element_wait_displayed(xpath=f"//span[text()='Definitivo']", tentativas=40):
                return
    
            # Verificar se aparece o popup de 'Operação abortada'
            if self.element_wait_displayed(xpath="//div[text()='Operação abortada']", tentativas=1):
                xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                mensagem_erro += self.element_get_text(xpath=xpath)
    
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def trocar_data_envio_faturamento(self, num_protocolo: str, data_entrega_faturamento_fisico: str) -> None:
        """
        Trocar a data de envio da conta.
        :param num_protocolo: Protocolo que foi pesquisado anteriormente;
        :param data_entrega_faturamento_fisico: Data que deve ser inserida no formato "DD/MM/YYYY".
        """
        mensagem_erro = 'Falha ao trocar data de envio. '
        try:
            # Click direito na primeira linha da tabela de protocolo
            if not self.element_right_click(xpath=f"//div[span='{num_protocolo}']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Protocolo não localizado."])
    
            # Click na opção "Alterar"
            if not self.element_click(xpath="(//div[contains(text(), 'Alterar')])"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Alterar) não localizado."])
    
            # Click na opção de alterar o Documento Convenio
            if not self.element_click(xpath="//div[contains(text(), 'Alterar data entrega faturamento físico')]"):
                mensagem_erro += "Opção (Alterar data entrega faturamento físico) não encontrada."
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
            # Insere a data de entrega
            if not self.element_left_click(xpath="//input[@name='DT_REGISTRO_FISICO']"):
                mensagem_erro += "Campo para inserir a data de entrega faturamento físico não encontrado."
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])
            data = re.sub(r'\D', '', data_entrega_faturamento_fisico)
            self.control_a()
            self.type_keys(list(data))
    
            # Clica em ok
            if not self.element_click(xpath="//button[@class='gwt-Button btn-blue']"):
                mensagem_erro += "Botão (OK) para confirmação da data de entrega faturamento físico não encontrado."
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
            # Verifica se a data foi registrada com sucesso
            # Pega exatamente a primeira ocorrência da data de entrega na linha da tabela de protocolo
            data_inserida = self.element_get_text(xpath=f"//span[contains(text(),'{data_entrega_faturamento_fisico}')]")
    
            # Remove qualquer caractere não numérico para realizar a comparação corretamente
            data_inserida = re.sub(r'\D', '', data_inserida)
            data_entrega_faturamento_fisico = re.sub(r'\D', '', data_entrega_faturamento_fisico)
    
            if data_inserida != data_entrega_faturamento_fisico:
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível confirmar a alteração."])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def inserir_observacao_protocolo(self, num_protocolo: str, observacao_protocolo: str) -> None:
        """
        Insere no Tasy as informações de processamento das contas de um protocolo específico.
        :param num_protocolo: Protocolo que foi pesquisado anteriormente;
        :param observacao_protocolo: Observação a ser inserida
        """
        mensagem_erro = 'Falha ao inserir observação no protocolo. '
        try:
            # Clica com botão direito no protocolo
            if not self.element_right_click(xpath=f"//div[span='{num_protocolo}']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Protocolo não localizado."])
    
            # Clica em alterar
            if not self.element_click(xpath="(//div[contains(text(), 'Alterar')])"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Alterar) não encontrado."])
    
            # Clica na caixa de texto de observação do protocolo
            if not self.element_click(xpath="//div[contains(text(), 'Observação do protocolo')]"):
                mensagem_erro += "Caixa de texto da observação do protocolo não localizada."
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
            xpath = "//*[@nmatributo='OBSERVACAO_PROTOCOLO']"
            if not self.element_set_text(xpath=xpath, text=observacao_protocolo):
                mensagem_erro += "Caixa de texto da observação do protocolo não localizada."
                raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
            # Confirma a inserção da observação do protocolo
            if not self.element_click(xpath="//button[span[contains(text(), 'OK')]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não encontrado."])
    
            # Verifica se a observação foi inserida corretamente, checando se a primeira conta da observação está
            # presente na tabela do tasy
            obs_primeira_conta = observacao_protocolo.split(',')[0]
            obs_inserida = self.element_get_text(xpath=f"//span[contains(text(),'{obs_primeira_conta}')]")
    
            if obs_inserida == '':
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Não foi possível confirmar a alteração."])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def enviar_lote_faturamento_tiss(self, seq_protocolo: str) -> str:
        """
        Clica com o botão direito no protocolo -> "TISS" -> "Enviar lote de faturamento" -> Clica em "Todas" -> Botão "OK"
        :param seq_protocolo: Sequência do Protocolo
        :return Diretório do arquivo XML baixado.
        """
        mensagem_erro = "Falha ao enviar lote de faturamento TISS. "
        try:
    
            # Aguarda tela com o protocolo carregar
            if not self.element_wait_displayed(xpath=f"//div[span='{seq_protocolo}']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Tabela com o protocolo {seq_protocolo} não localizada."])
    
            # Acessa a tela de "Enviar lote faturamento TISS"
            self.type_keys([Keys.SHIFT, Keys.ALT, "e"])
    
            # Aguardar o pop-up para confirmar Atualizar contas TISS
            xpath = "//div[@class='dialog-title']//span[text()='Atualizar contas TISS']"
            if not self.element_wait_displayed(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up para atualizar contas TISS não localizado."])
    
            # Seleciona a opção "Todas"
            xpath = "//div[input[@name='radio_IE_SOMENTE_PENDENTES']]//div[contains(text(),'Todas')]"
            if not self.element_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Todas) não localizado."])
    
            # Clica em "OK"
            if not self.element_click(xpath="//button[span[contains(text(),'OK')]]"):
                raise Exception([LOG_EX_SISTEMA,  mensagem_erro + "Botão (OK) não localizado."])
    
            # Aguardar a página de informação de contas atualizadas
            xpath = "//div[@class='dialog-content']//div[text()='Contas atualizadas com sucesso!']"
            if not self.element_wait_displayed(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA,  mensagem_erro + "Pop-up de confirmação não localizado."])
    
            # Clicar em "OK"
            if not self.element_click(xpath="//button[contains(text(),'Ok')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])
    
            # Aguardar a janela confirmação
            xpath = "//div[contains(text(),'Deseja gerar o(s) arquivo(s) de Guia de')]"
            if not self.element_wait_displayed(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Pop-up para gerar Guia de consulta não localizado."])
    
            # Clicar em "OK"
            if not self.element_click("//button[contains(text(),'Ok')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (OK) não localizado."])
    
            # Aguarda o download ser concluído
            arquivo = self.esperar_conclusao_download(extensao_arquivo='.xml')
    
            return arquivo
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)
    
    def adicionar_anexo(self, dir_anexo: str) -> None:
        """
        Acessa a aba de anexos e adiciona o anexo.
        :param dir_anexo: Diretório do arquivo a ser adicionado
        """
        mensagem_erro = "Falha ao adicionar anexo ao protocolo. "
        try:
            # Valida se a tela de anexos está carregada
            xpath = "//div[@class='wtitle-container margin']//div[contains(text(),'Anexo')]"
            if not self.find_element(xpath, By.XPATH, ensure_visible=True, ensure_clickable=True):
                # Clica nos 3 pontinhos para abrir as opções do menu
                if not self.element_click("//div[div[div[div[contains(text(),'Anexo')]]]]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Menu (...) não localizado."])
    
                # Clica em anexo
                if not self.element_click("//div[contains(text(),'Anexo')]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Menu (Anexo) não localizado."])
    
            # Pegar a quantidade de arquivos antes de realizar o upload
            qt_arquivos_antes = int(self.element_get_text(xpath="//i[@id = 'totalRecordsPageFinish']"))
    
            # Clica em adicionar
            if not self.element_click("//*[contains(text(),'Adicionar')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Adicionar) não localizado."])
    
            # Seleciona o anexo
            self.upload_arquivo_background(xpath_upload="//*[@id='DS_ANEXO']", caminho_arquivo=dir_anexo)
    
            # Clica em salvar
            if not self.element_click("//div[div[div[span[contains(text(),'Salvar')]]]]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Salvar) não localizado."])
    
            # Espera a página concluir o processamento
            qt_arquivos_depois = 0
            for i in range(60):
                n = self.element_get_text(xpath="//i[@id = 'totalRecordsPageFinish']")
                qt_arquivos_depois = int(n) if n != '' else 0
                if qt_arquivos_depois > qt_arquivos_antes:
                    break
                self.wait(500)
            if not qt_arquivos_depois > qt_arquivos_antes:
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Timeout ao confirmar o upload do anexo."])
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self)
            raise ValueError(error_message)

