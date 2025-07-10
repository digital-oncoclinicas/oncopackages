from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA, RPA_DIR_DOWNLOADS
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By, Keys
import re


class ProtocoloConvenio(Tasy):
    
    def pesquisar_protocolo(self, protocolo: str) -> None:
        """
        Realiza a pesquisa pela sequência do protocolo na função Protocolo Convênio do Tasy.
        Args:
             protocolo: str: Sequência do protocolo.
        """
        # Verifica se a tela de filtros esta na tela
        if not self.bot.search_element(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=10):
            # Clicar no ícone de Filtro que fica no canto superior esquerdo
            self.bot.element_click(xpath="//*[contains(@class,'filter-icon')]")

            # Espera a tela carregar
            if not self.bot.search_element(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=20):
                raise Exception([LOG_EX_SISTEMA, "Tela de pesquisa não localizada."])

        # Preencher o campo 'Sequência protocolo'
        if not self.bot.element_set_text(xpath="//input[@name='NR_SEQ_PROTOCOLO']", text=protocolo, delay=1000):
            raise Exception([LOG_EX_SISTEMA, f"Campo (Sequência protocolo) não localizado."])
        self.bot.tab()

        # Clica no botão Filtrar
        if not self.bot.element_click(xpath="//button[contains(text(), 'Filtrar')]"):
            raise Exception([LOG_EX_SISTEMA, f"Botão (Filtrar) não localizado."])

        # Aguarda a tela carregar
        if self.bot.search_element(xpath=f"//div[span='{protocolo}']"):
            return

        # Aguarda a tela carregar
        if self.bot.search_element(xpath=f"//span[text()='Seu filtro não encontrou nenhum resultado.']"):
            raise Exception([LOG_EX_NEGOCIO, "Seu filtro não encontrou nenhum resultado."])

        raise Exception([LOG_EX_SISTEMA, "Resultado não localizado."])
    
    def pesquisar_convenio(self, convenio: str) -> None:
        """
        Função pesquisa pelos protocolos associados ao convênio.
        Args:
            convenio: Nome do convênio filtrado
        """
        # Verifica se a tela de filtros já está aberta
        if not self.bot.search_element(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=10):
            # Clicar no ícone de Filtro que fica no canto superior esquerdo
            self.bot.element_click(xpath="//*[contains(@class,'filter-icon')]")

            # Espera a tela carregar
            if not self.bot.search_element(xpath="//input[@name='NR_SEQ_PROTOCOLO']", tentativas=10):
                raise Exception([LOG_EX_SISTEMA, "Tela de pesquisa não localizado."])

        # Preencher o campo 'Convênio'
        self.bot.element_click(xpath="//div[input[@name='CD_CONVENIO']]", delay=500)
        if not self.bot.element_click(xpath=f"//a[span[text()='{convenio}']]", delay=250):
            raise Exception([LOG_EX_SISTEMA, f"Convênio ({convenio}) não localizado."])

        # Clica no botão Filtrar
        self.bot.element_click(xpath="//button[contains(text(), 'Filtrar')]")

        # Aguarda a tela carregar
        if self.bot.search_element(xpath="//*[contains(text(),'Adicionar')]", tentativas=30):
            return

        raise Exception([LOG_EX_SISTEMA, "Resultado não localizado."])
    
    def acessar_protocolo(self, seq_protocolo: str) -> None:
        """
        Realiza a pesquisa pela sequência do protocolo na função Protocolo Convênio do Tasy.
        Args:
             seq_protocolo: str: sequência do protocolo.
        """
        # Duplo click na linha do protocolo
        self.bot.element_double_click(xpath=f"//div[span='{seq_protocolo}']")

        if not self.bot.find_element("//span[contains(text(), 'Procedimentos')]", By.XPATH, ensure_visible=True):
            raise Exception([LOG_EX_SISTEMA, "Tela de detalhes do protocolo não localizada."])
    
    def alterar_documento_convenio(self, protocolo: str, desc_doc_convenio: str) -> None:
        """
        Função altera o campo de Documento Convênio
        Args:
            protocolo: Sequencia do protocolo
            desc_doc_convenio: Conteúdo a ser adicionado ou substituído no campo
        """
        # Clica com o botão direito do mouse na linha do protocolo
        if not self.bot.element_right_click(xpath=f"//div[span='{protocolo}']"):
            raise Exception([LOG_EX_SISTEMA, "Protocolo não localizada."])

        # Click na opção "Alterar"
        self.bot.find_element("(//div[contains(text(), 'Alterar')])[2]", By.XPATH).click()

        # Click na opção de alterar o Documento Convenio
        self.bot.find_element("//div[contains(text(), 'Alterar o documento do convênio')]", By.XPATH).click()

        # Aguarda o pop-up abrir
        if not self.bot.find_element("//span[contains(text(),'Alterar doc. convênio')]", By.XPATH):
            raise Exception([LOG_EX_SISTEMA, "Pop-up para altera doc convenio não foi localizado."])
        self.bot.wait(1000)

        # Insere a sequência do Protocolo no campo
        xpath = "//input[@name='NR_SEQ_DOC_CONV']"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).clear()
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(desc_doc_convenio)

        # Clica em" OK "
        self.bot.find_element("//button[span[contains(text(),'OK')]]", By.XPATH).click()

        # Valida a alteração do documento convênio
        xpath = fr"//div[span[text()='{desc_doc_convenio}']]"
        if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
            raise Exception([LOG_EX_SISTEMA, "Alteração doc. convênio não localizada."])
    
    def adicionar_protocolo(self, tipo_protocolo: str, data_referencia: str, identificacao_protocolo: str,
                            periodo_inicial_conta: str, periodo_final_conta: str) -> str:
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
        # Clica no botão adicionar para criar um protocolo
        if not self.bot.element_click(xpath="//*[span[contains(text(),'Adicionar')]]", delay=1000):
            raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])

        # Pega o número do campo 'Sequência'
        protocolo = self.bot.element_get_value(xpath="//input[@name='NR_SEQ_PROTOCOLO']", delay=1000)

        # Preencher o campo 'Tipo protocolo'
        self.bot.element_click(xpath="//div[input[@name='IE_TIPO_PROTOCOLO']]")
        if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_protocolo}']]", delay=250):
            raise Exception([LOG_EX_NEGOCIO, f"Tipo protocolo ({tipo_protocolo}) não localizado."])

        # Preenche o campo 'Data referência'
        self.bot.element_set_text(xpath="//input[@name='DT_MESANO_REFERENCIA']", text=data_referencia)

        # Preencher o campo 'Identificação protocolo'
        identificacao_protocolo = f"{protocolo}_{identificacao_protocolo}"
        self.bot.element_set_text(xpath="//input[@name='NR_PROTOCOLO']", text=identificacao_protocolo)

        # Preenche o campo 'Período inicial conta'
        self.bot.element_set_text(xpath="//input[@name='DT_PERIODO_INICIAL']", text=periodo_inicial_conta)

        # Preenche o campo 'Período final conta'
        self.bot.element_set_text(xpath="//input[@name='DT_PERIODO_FINAL']", text=periodo_final_conta)

        # Clica no botão 'Salvar'
        if not self.bot.element_left_click(xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])

        # Verificar se salvou com sucesso
        if self.bot.search_element(xpath=f"//span[text()='{protocolo}']", tentativas=40):
            return protocolo

        # Verificar se aparece o popup de 'Operação abortada'
        mensagem_erro = "Adição não confirmada."
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)

        raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
    def mudar_status_protocolo(self, protocolo: str) -> None:
        """
        Função muda o status do protocolo para "Definitivo"
        Args:
            protocolo: Sequência do protocolo
        """
        # Clica com o botão direito do mouse na linha do protocolo
        if not self.bot.element_right_click(xpath=f"//div[span='{protocolo}']"):
            raise Exception([LOG_EX_SISTEMA, "Protocolo não localizada."])

        # Click na opção "Mudar status"
        if not self.bot.element_click(xpath="//div[text()='Muda status']"):
            raise Exception([LOG_EX_SISTEMA, f"Menu (Mudar status) não localizado."])

        # Verificar se salvou com sucesso
        if self.bot.search_element(xpath=f"//span[text()='Definitivo']", tentativas=40):
            return

        # Verificar se aparece o popup de 'Operação abortada'
        mensagem_erro = "Alteração não confirmada."
        if self.bot.search_element(xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro = self.bot.element_get_text(xpath=xpath)

        raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
    def trocar_data_envio_faturamento(self, num_protocolo: str, data_entrega_faturamento_fisico: str) -> None:
        """
        Trocar a data de envio da conta.
        :param num_protocolo: Protocolo que foi pesquisado anteriormente;
        :param data_entrega_faturamento_fisico: Data que deve ser inserida no formato "DD/MM/YYYY".
        """
        # Click direito na primeira linha da tabela de protocolo
        if not self.bot.element_right_click(xpath=f"//div[span='{num_protocolo}']"):
            raise Exception([LOG_EX_SISTEMA, "Protocolo não localizado."])

        # Click na opção "Alterar"
        if not self.bot.element_click(xpath="(//div[contains(text(), 'Alterar')])"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Alterar) não localizado."])

        # Click na opção de alterar o Documento Convenio
        if not self.bot.element_click(xpath="//div[contains(text(), 'Alterar data entrega faturamento físico')]"):
            mensagem_erro = "Opção (Alterar data entrega faturamento físico) não encontrada."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        # Insere a data de entrega
        if not self.bot.element_left_click(xpath="//input[@name='DT_REGISTRO_FISICO']"):
            mensagem_erro = "Campo para inserir a data de entrega faturamento físico não encontrado."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
        data = re.sub(r'\D', '', data_entrega_faturamento_fisico)
        self.bot.control_a()
        self.bot.type_keys(list(data))

        # Clica em ok
        if not self.bot.element_click(xpath="//button[@class='gwt-Button btn-blue']"):
            mensagem_erro = "Botão (OK) para confirmação da data de entrega faturamento físico não encontrado."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        # Verifica se a data foi registrada com sucesso
        # Pega exatamente a primeira ocorrência da data de entrega na linha da tabela de protocolo
        data_inserida = self.bot.element_get_text(xpath=f"//span[contains(text(),'{data_entrega_faturamento_fisico}')]")

        # Remove qualquer caractere não numérico para realizar a comparação corretamente
        data_inserida = re.sub(r'\D', '', data_inserida)
        data_entrega_faturamento_fisico = re.sub(r'\D', '', data_entrega_faturamento_fisico)

        if data_inserida != data_entrega_faturamento_fisico:
            raise Exception([LOG_EX_SISTEMA, "Alteração não confirmada."])
    
    def inserir_observacao_protocolo(self, num_protocolo: str, observacao_protocolo: str) -> None:
        """
        Insere no Tasy as informações de processamento das contas de um protocolo específico.
        :param num_protocolo: Protocolo que foi pesquisado anteriormente;
        :param observacao_protocolo: Observação a ser inserida
        """
        # Clica com botão direito no protocolo
        if not self.bot.element_right_click(xpath=f"//div[span='{num_protocolo}']"):
            raise Exception([LOG_EX_SISTEMA, "Protocolo não localizado."])

        # Clica em alterar
        if not self.bot.element_click(xpath="(//div[contains(text(), 'Alterar')])"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Alterar) não encontrado."])

        # Clica na caixa de texto de observação do protocolo
        if not self.bot.element_click(xpath="//div[contains(text(), 'Observação do protocolo')]"):
            mensagem_erro = "Caixa de texto da observação do protocolo não localizada."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        xpath = "//*[@nmatributo='OBSERVACAO_PROTOCOLO']"
        if not self.bot.element_set_text(xpath=xpath, text=observacao_protocolo):
            mensagem_erro = "Caixa de texto da observação do protocolo não localizada."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        # Confirma a inserção da observação do protocolo
        if not self.bot.element_click(xpath="//button[span[contains(text(), 'OK')]]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (OK) não encontrado."])

        # Verifica se a observação foi inserida corretamente, checando se a primeira conta da observação está
        # presente na tabela do tasy
        obs_primeira_conta = observacao_protocolo.split(',')[0]
        obs_inserida = self.bot.element_get_text(xpath=f"//span[contains(text(),'{obs_primeira_conta}')]")

        if obs_inserida == '':
            raise Exception([LOG_EX_SISTEMA, "Alteração não confirmada."])
        
    def enviar_lote_faturamento_tiss(self, protocolo: str) -> str:
        """
        Clica com o botão direito no protocolo -> "TISS" -> "Enviar lote de faturamento" -> Clica em "Todas" -> Botão "OK"
        :param protocolo: Sequência do Protocolo;
        :return Diretório do arquivo XML baixado.
        """
        # Aguarda tela com o protocolo carregar
        if not self.bot.search_element(xpath=f"//div[span='{protocolo}']"):
            raise Exception([LOG_EX_SISTEMA, f"Tabela com o protocolo {protocolo} não localizada."])

        # Acessa a tela de "Enviar lote faturamento TISS"
        self.bot.type_keys([Keys.SHIFT, Keys.ALT, "e"])

        # Aguardar o pop-up para confirmar Atualizar contas TISS
        xpath = "//div[@class='dialog-title']//span[text()='Atualizar contas TISS']"
        if not self.bot.search_element(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, "Pop-up para atualizar contas TISS não localizado."])

        # Seleciona a opção "Todas"
        xpath = "//div[input[@name='radio_IE_SOMENTE_PENDENTES']]//div[contains(text(),'Todas')]"
        if not self.bot.element_click(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, "Botão (Todas) não localizado."])

        # Clica em "OK"
        if not self.bot.element_click(xpath="//button[span[contains(text(),'OK')]]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (OK) não localizado."])

        # Aguardar a página de informação de contas atualizadas
        xpath = "//div[@class='dialog-content']//div[text()='Contas atualizadas com sucesso!']"
        if not self.bot.search_element(xpath=xpath, tentativas=60):
            raise Exception([LOG_EX_SISTEMA, "Pop-up de confirmação não localizado."])

        # Clicar em "OK"
        if not self.bot.element_click(xpath="//button[contains(text(),'Ok')]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (OK) não localizado."])

        # Continuar mesmo que apareça esse outro popup
        xpath = "//div[contains(text(),'O valor total do protocolo não bate com o valor total das guias!')]"
        if self.bot.search_element(xpath=xpath, tentativas=10):
            if not self.bot.element_click(xpath="//button[contains(text(),'Ok')]"):
                raise Exception([LOG_EX_SISTEMA, "Botão (OK) não localizado."])

        # Aguardar a janela confirmação
        xpath = "//div[contains(text(),'Deseja gerar o(s) arquivo(s) de Guia de')]"
        if not self.bot.search_element(xpath=xpath):
            raise Exception([LOG_EX_NEGOCIO, "Pop-up para gerar Guia de consulta não localizado."])

        # Conta a quantidade de arquivos na pasta de downloads com a mesma extensão do arquivo que será baixado
        qt_arquivos_antes = self.bot.get_file_count(file_extension=".xml") + self.bot.get_file_count(file_extension=".zip")

        # Clicar em "OK"
        if not self.bot.element_click(xpath="//button[contains(text(),'Ok')]", delay=2000):
            raise Exception([LOG_EX_SISTEMA, "Botão (OK) não localizado."])

        # Aguarda o início da geração do arquivo
        xpath = "(//div[contains(@class, 'w-loader-popup')])[3]"
        self.bot.search_element(xpath=xpath, tentativas=20)

        # Espera a conclusão do download por até 60 segundos
        qt_arquivos_apos = 0
        for i in range(120):
            qt_arquivos_apos = self.bot.get_file_count(file_extension=".xml") + self.bot.get_file_count(file_extension=".zip")
            if qt_arquivos_apos > qt_arquivos_antes:
                break
            self.bot.wait(500)

        if qt_arquivos_apos <= qt_arquivos_antes:
            raise Exception([LOG_EX_SISTEMA, f'Timeout ao esperar a conclusão do download.'])

        # Pega o diretório completo do arquivo baixado
        arquivo = self.bot.get_last_created_file(path=RPA_DIR_DOWNLOADS)

        return arquivo

    def adicionar_anexo(self, dir_anexo: str) -> None:
        """
        Acessa a aba de anexos e adiciona o anexo.
        :param dir_anexo: Diretório do arquivo a ser adicionado
        """
        # Valida se a tela de anexos está carregada
        xpath = "//div[@class='wtitle-container margin']//div[contains(text(),'Anexo')]"
        if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True, ensure_clickable=True):
            # Clica na aba "Anexo"
            if not self.bot.element_click(xpath="//div[span[text()='Anexo']]", tentativas=2):
                # Clica nos 3 pontinhos para abrir as opções do menu
                if not self.bot.element_click(xpath="//div[div[div[div[contains(text(),'Anexo')]]]]"):
                    raise Exception([LOG_EX_SISTEMA, "Menu (...) não localizado."])

                # Clica no menu "Anexo"
                if not self.bot.element_click(xpath="//div[contains(text(),'Anexo')]"):
                    raise Exception([LOG_EX_SISTEMA, "Menu (Anexo) não localizado."])

        # Pegar a quantidade de arquivos antes de realizar o upload
        qt_arquivos_antes = int(self.bot.element_get_text(xpath="//i[@id = 'totalRecordsPageFinish']"))

        # Clicar na aba 'Anexos do protocolo do convênio'
        self.bot.search_element(xpath="//div[span[text()='Anexos do protocolo do convênio']]", delay=500).click()

        # Clica em adicionar
        if not self.bot.element_click(xpath="//*[contains(text(),'Adicionar')]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])

        # Seleciona o anexo
        self.bot.upload_arquivo_background(xpath_upload="//*[@id='DS_ANEXO']", caminho_arquivo=dir_anexo)

        # Seleciona o tipo do anexo
        self.bot.element_click(xpath="//div[input[@name='IE_TIPO_DOCUMENTO_TISS']]", delay=500)
        if not self.bot.element_click(xpath=f"//a[span[contains(text(),'Comprovante de elegibilidade')]]", delay=500):
            raise Exception([LOG_EX_NEGOCIO, f"Tipo de anexo 'Comprovante de elegibilidade' não localizado."])

        # Clica em salvar
        if not self.bot.element_click(xpath="//div[div[div[span[contains(text(),'Salvar')]]]]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])

        # Adiciona uma camada de resiliência.
        # Valida se o popup de anexo faltante apareceu e tenta fazer o upload novamente
        if self.bot.search_element(xpath="//div[a[text()='O formulário não foi salvo.']]"):
            self.bot.upload_arquivo_background(xpath_upload="//*[@id='DS_ANEXO']", caminho_arquivo=dir_anexo)
            # Clica em salvar
            if not self.bot.element_click(xpath="//div[div[div[span[contains(text(),'Salvar')]]]]"):
                raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])

        # Espera a página concluir o processamento
        qt_arquivos_depois = 0
        for i in range(60):
            n = self.bot.element_get_text(xpath="//i[@id = 'totalRecordsPageFinish']")
            qt_arquivos_depois = int(n) if n != '' else 0
            if qt_arquivos_depois > qt_arquivos_antes:
                break
            self.bot.wait(500)
        if not qt_arquivos_depois > qt_arquivos_antes:
            raise Exception([LOG_EX_SISTEMA, "Timeout ao confirmar o upload do anexo."])

    def gerar_titulo(self, protocolo: str, data_emissao: str = "", data_vencimento: str = ""):
        """
        Gerar título do protocolo.
        """
        # Validar que o protocolo está carregado na tela
        if not self.bot.search_element(f"//div[span='{protocolo}']"):
            raise Exception([LOG_EX_SISTEMA, "Protocolo não localizado na tela."])

        # Aperta ALT+Q para acessar a tela de Gerar Titulo Receber
        self.bot.type_keys([Keys.ALT, "q"])

        # Aguarda a tela de Gerar titulo carregar
        if not self.bot.search_element("//button[span[text()='Gerar título receber']]"):
            raise Exception([LOG_EX_SISTEMA, "Tela de Gerar titulo não localizada."])

        # Preencher a data de emissão
        if data_emissao:
            if not self.bot.element_set_text(xpath="//input[@name='DT_EMISSAO']", text=data_emissao):
                raise Exception([LOG_EX_SISTEMA, "Campo de data de emissão não localizada."])

        # Preencher a data de vencimento
        if data_vencimento:
            if not self.bot.element_set_text(xpath="//input[@name='DT_VENCIMENTO']", text=data_vencimento):
                raise Exception([LOG_EX_SISTEMA, "Campo de data de vencimento não localizado."])

        # Clica em Gerar titulo receber
        if not self.bot.element_click("//button[span[text()='Gerar título receber']]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Gerar título receber) não localizado."])

        # Espera a linha do título aparecer na tabela de títulos
        if not self.bot.search_element(f"//div[div[div[span[text()='Real']]]]", tentativas=120):
            # Verifica se possuí algum pop-up
            xpath = "//div[contains(text(),'A data de emissão está fora do período final do protocolo/conta.')]"
            if self.bot.search_element(xpath=xpath, tentativas=4):
                if not self.bot.element_click("//button[text()='Sim']", tentativas=2):
                    raise Exception([LOG_EX_SISTEMA, "Botão Sim do pop-up não localizado."])
            else:
                raise Exception([LOG_EX_SISTEMA, "Botão OK não localizado."])

        # Fecha a página de Gerar Títulos
        if not self.bot.element_click("//div[span[text()='Gerar Título Receber']]/button"):
            raise Exception([LOG_EX_SISTEMA, "Botão fechar não localizado."])

        # Valida se retornou para a tela da função "Protocolo Convênio"
        xpath = f"//div[span='{protocolo}']"
        if not self.bot.search_element(xpath=xpath):
            raise Exception([LOG_EX_SISTEMA, "Tela com o protocolo não localizada."])

    def retornar_para_tela_do_protocolo(self, protocolo: str) -> None:
        """
        Retorna para a tela inicial do protocolo após terminar de adicionar o anexo.
        :param protocolo: Sequência do protocolo
        """
        for i in range(5):
            xpath = "(//div[div[contains(text(), 'Protocolo')] and contains(@class, 'wtab')])[1]"
            if not self.bot.element_double_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, "Botão (Protocolo) não localizado."])
            if self.bot.search_element(xpath=f"//div[span='{protocolo}']"):
                break
        raise Exception([LOG_EX_SISTEMA, ""])
