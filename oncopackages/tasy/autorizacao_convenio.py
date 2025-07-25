from config import LOG_EX_NEGOCIO, LOG_EX_SISTEMA
from oncopackages.tasy.tasy import Tasy
from botcity.web.bot import By, Keys
from datetime import datetime


class AutorizacaoConvenio(Tasy):
        
    def pesquisar_sequencia_autorizacao(self, seq_autorizacao: str):
        """
        Realiza a pesquisa pela sequência da autorização na função Autorização Convênio do Tasy.
        :param seq_autorizacao: Sequência da autorização.
        """
        # Espera a tela carregar
        if not self.bot.find_element("(//button[contains(text(), 'Ações do filtro')])[2]", By.XPATH, ensure_clickable=True):
            raise Exception([LOG_EX_SISTEMA, "Botão (Ações do filtro) não localizado."])
        self.bot.wait(1000)
    
        # Clicar no ícone de Filtro que fica no canto superior esquerdo
        xpath = "//tasy-wlabel[@uib-tooltip='Filtros em uso (Ctrl + Alt + F)'][@tooltip-append-to-body='true']"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).click()
    
        # Espera a tela carregar
        if not self.bot.find_element("//button[contains(text(), 'Filtrar')]", By.XPATH, ensure_clickable=True):
            raise Exception([LOG_EX_SISTEMA, "Tela de pesquisa não localizada."])
    
        # Insere a sequência da autorização no campo 'Autorização'
        xpath = "//input[@name='NR_SEQUENCIA']"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).clear()
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(seq_autorizacao)
    
        # Clica no botão Filtrar
        self.bot.find_element("//button[contains(text(), 'Filtrar')]", By.XPATH).click()
    
        # Verificar se a autorização foi localizada
        if not self.bot.find_element(f"//div[span='{seq_autorizacao}']", By.XPATH):
            raise Exception([LOG_EX_NEGOCIO, "Autorização não localizada."])
    
    def excluir_autorizacao(self):
        """
        Exclui a autorização que estiver selecionada na tabela de resultados da função Autorização Convênio.
        """
        # Clicar no menu 'Excluir' que fica no canto superior direito da tela
        xpath = "//span[contains(text(), 'Excluir')]"
        self.bot.find_element(xpath, By.XPATH, ensure_visible=True, ensure_clickable=True).click()
    
        # Verificar se aparece um popup com o título 'Confirmação'
        xpath = "//div[contains(text(), 'Deseja excluir o registro?')]"
        if not self.bot.find_element(xpath, By.XPATH, waiting_time=3000, ensure_visible=True):
            raise Exception([LOG_EX_NEGOCIO, "Exclusão negada pelo Tasy."])
    
        # Clica em 'Ok' no popup de confirmação
        xpath = "//button[contains(text(), 'Ok')]"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
    
        # Verificar se a linha da tabela foi excluída
        for i in range(12):
            if not self.bot.find_element("(//div[@data-row-idx=0])[2]", By.XPATH, ensure_visible=True, waiting_time=0):
                return
            self.bot.wait(500)
    
        raise Exception([LOG_EX_NEGOCIO, "Falha após confirmar a exclusão."])
    
    def adicionar_historico_autorizacao(self, tipo_historico: str, historico: str):
        """
        Função que acessa a opção de histórico da Autorização e Adicionar um Histórico nos registros.
        :param tipo_historico: O tipo de Histórico que será selecionado
        :param historico: O Texto que será inserido no campo Histórico
        """
        # Espera a tela carregar com a opção de Histórico
        if not self.bot.find_element("//*[@id='pages']//*[@tab-tooltip='Histórico']", By.XPATH, ensure_clickable=True):
            raise Exception([LOG_EX_SISTEMA, "Menu Histórico localizado."])
        self.bot.wait(1000)
    
        # Clicar no Histórico no menu da lateral esquerda
        xpath = "//*[@id='pages']//*[@tab-tooltip='Histórico']"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).click()
    
        # Espera aparecer Botão 'Adicionar' para Adicionar Histórico
        xpath = "(//button/span[contains(text(), 'Adicionar')])[2]"
        if not self.bot.find_element(xpath, By.XPATH, ensure_clickable=True):
            raise Exception([LOG_EX_SISTEMA, "Botão de Adicionar não Localizado."])
    
        # Clicar na opção 'Adicionar'
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
    
        # Espera a tela carregar a lista suspensa com o Tipo de Histórico
        xpath = "//div[input[@name='NR_SEQ_TIPO_HIST']]"
        if not self.bot.find_element(xpath, By.XPATH, ensure_clickable=True):
            raise Exception([LOG_EX_SISTEMA, "Lista com os Tipo de Histórico não localizada."])
        self.bot.wait(500)
    
        # Clica na lista suspensa com o Tipo de Histórico
        self.bot.find_element(xpath, By.XPATH).click()
    
        # Verificar se a opção 'Informações Internas' está na lista suspensa
        if not self.bot.element_click(xpath=f"//a/span[contains(text(), '{tipo_historico}')]", delay=1000):
            raise Exception([LOG_EX_NEGOCIO, f"Tipo de histórico({tipo_historico}) não localizado."])
    
        # Verificar se a área de digitar o texto com o histórico está disponível
        xpath = "//div//textarea[@name='DS_HISTORICO']"
        if not self.bot.find_element(xpath, By.XPATH):
            raise Exception([LOG_EX_SISTEMA, "Campo para digitar o Histórico não localizado"])
    
        # Preencher campo Histórico
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(f"{historico}")
    
        # Verificar se o botão de Salvar está disponível na tela
        xpath = "//div[div[div[div[span[text() = 'Histórico']]]]]//*/tasy-wbutton[@text='Salvar']"
        if not self.bot.find_element(xpath, By.XPATH, ensure_clickable=True):
            raise Exception([LOG_EX_SISTEMA, "Botão Salvar não localizado."])
    
        # Click em Salvar
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
    
        # Espera o processamento concluir
        if not self.bot.search_element(xpath="//*[text() = 'Adicionar']"):
            raise Exception([LOG_EX_SISTEMA, "Não foi possível confirmar a inclusão do histórico."])
    
    def alterar_estagio(self, nome_estagio: str, motivo: str = None, autorizacao: str = None):
        """
        Função que altera o Estágio da Autorização no Tasy.
        :param nome_estagio: Nome do estágio a ser alterado.
        :param motivo: Motivo da alteração do estágio.
        :param autorizacao: Sequência da autorização. Necessário caso haja mais de uma autorização na tabela de autorizações.
        """
        # Verifica se está na tela inicial da função "Autorização Convênio"
        if not self.bot.search_element(xpath="//*[contains(text(),'Relatórios')]"):
            mensagem_erro = "Tela inicial da função Autorização Convênio não localizada."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        # Acionar o atalho [F9] para acionar a tela de Alterar Estágio
        if autorizacao and not self.bot.element_click(xpath=f"//div[div[div[span[text() = '{autorizacao}']]]]"):
            raise Exception([LOG_EX_SISTEMA, "Autorização não localizada."])
        self.bot.key_fx(9)
    
        # Seleciona o Estágio
        xpath = "//div[div[div[div[span[text() = 'Alterar estágio']]]]]//div[input[@name='NR_SEQ_ESTAGIO']]"
        self.bot.element_click(xpath=xpath, delay=1000)
        if not self.bot.element_click(xpath=f"//a[span[contains(text(), '{nome_estagio}')]]", delay=500):
            raise Exception([LOG_EX_NEGOCIO, f"Estágio ({nome_estagio}) não localizado."])
    
        # Selecionar o Motivo da Alteração de estágio caso a variável seja diferente de Null e o campo esteja habilitado
        xpath = "//div[input[@name='CD_MOTIVO_ESTAGIO'] and @class ='w-listbox w-listbox-dropdown']"
        if motivo and self.bot.find_element(xpath, By.XPATH, waiting_time=2000):
            # Seleciona o 'Motivo'
            self.bot.element_click(xpath=xpath, delay=1000)
            if not self.bot.element_click(xpath=f"//a[span[contains(text(),'{motivo}')]]", delay=500):
                mensagem_erro = f"Motivo ({motivo}) não localizado."
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro])
    
        # Clicar em OK
        xpath = "//button[span[contains(text(), 'OK')]]"
        if not self.bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True):
            raise Exception([LOG_EX_SISTEMA, "Botão (OK) para alterar o estágio não localizado."])
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).click()
    
        # Verificar se aparece o popup de confirmação
        xpath = "//div[text()='Confirmação' or text()='Informação']"
        if self.bot.search_element(xpath=xpath, tentativas=4):
            self.bot.find_element("//button[text()='Ok']", By.XPATH).click()
    
        # Verificar se o estágio foi alterado
        if autorizacao:
            xpath = f"//div[div[div[span[text() = '{autorizacao}']]] and div[div[span[span[contains(text(), '{nome_estagio}')]]]]]"
        else:
            xpath = f"//span/span[contains(text(), '{nome_estagio}')]"
        if not self.bot.find_element(xpath, By.XPATH, waiting_time=20000):
            raise Exception([LOG_EX_NEGOCIO, "Timeout ao confirmar a alteração."])
    
    def inserir_solicitacao(self, solicitacao: str):
        """
        Insere o número da solicitação na autorização, no Tasy.
        :param solicitacao: Número da solicitação que foi criada no site do convênio.
        """
        # Clica em 'Ver' no canto superior direito
        self.bot.find_element("//span[text() = 'Ver']", By.XPATH, ensure_clickable=True).click()
    
        # Insere o número da solicitação no campo 'Numero do protocolo'
        self.bot.find_element("//input[@name='CD_SENHA_PROVISORIA']", By.XPATH).clear()
        self.bot.find_element("//input[@name='CD_SENHA_PROVISORIA']", By.XPATH).send_keys(solicitacao)
    
        # Insere a data atual no campo 'Data envio'
        data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.bot.find_element("//input[@name='DT_ENVIO']", By.XPATH).clear()
        self.bot.find_element("//input[@name='DT_ENVIO']", By.XPATH).send_keys(data_atual)
    
        # Clica em 'Salvar'
        xpath = "//div[div[div[span[text() = 'Salvar']]]]"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
    
        # Verificar se a alteração foi salva
        if not self.bot.find_element("//span[text() = 'Ver']", By.XPATH, ensure_visible=True):
            raise Exception([LOG_EX_NEGOCIO, "Timeout ao confirmar a alteração."])
    
    def atualizar_procedimentos(self, lista_procedimentos: list, bd_tasy):
        """
        Atualizar os procedimentos da autorização no Tasy.
        :param lista_procedimentos: Lista com Procedimento, quantidade solicitada e quantidade autorizada.
        :param bd_tasy: Objeto do banco de dados do Tasy.
        """
        for item in lista_procedimentos:
            # Set de variáveis
            procedimento, qt_solicitada, qt_autorizada = eval(item)
    
            # Se o procedimento não for encontrado, deve ser adicionado.
            if not self.bot.find_element(f"//span[text() = '{procedimento}']", By.XPATH, waiting_time=3000):
                # Pega o código do procedimento no banco de dados do robô
                proc_interno = bd_tasy.procedimento_interno(procedimento)
    
                self.adicionar_procedimento(
                    cd_procedimento_interno=proc_interno, qt_autorizada=qt_autorizada, qt_solicitada=qt_solicitada
                )
    
            # Se o procedimento já existe, apenas atualiza a quantidade autorizada
            else:
                # Clica na linha do procedimento
                xpath = f"//div[div[div[span[text() = '{procedimento}']]]]"
                if not self.bot.element_left_click(xpath=xpath):
                    raise Exception([LOG_EX_SISTEMA, f"Procedimento ({procedimento}) não localizado."])
    
                # Clica no desenho de um lapis no fim da linha do procedimento selecionado
                if not self.bot.element_left_click(xpath="//a[@id='_inlineEdit']"):
                    raise Exception([LOG_EX_SISTEMA, f"Botão para editar o procedimento não localizado."])
    
                # Preenche o campo 'Quantidade autorizada'
                self.bot.find_element("//input[@name='QT_AUTORIZADA']", By.XPATH).clear()
                self.bot.find_element("//input[@name='QT_AUTORIZADA']", By.XPATH).send_keys(qt_autorizada)
    
                # Clica em 'Salvar'
                if not self.bot.element_click(xpath="//button[text() = 'Salvar']"):
                    raise Exception([LOG_EX_NEGOCIO, "Botão (Salvar) não localizado."])
    
                # Confirma a alteração
                xpath = f"//div[div[div[span[text() = '{procedimento}' or text() = '']]]]/div/div/span[text()='{qt_autorizada}']"
                if not self.bot.find_element(xpath, By.XPATH):
                    mensagem_erro = f"Timeout ao confirmar a alteração do procedimento ({procedimento})."
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
                # Se não houver essa espera o Tasy apresenta falha ao salvar
                self.bot.wait(2000)
    
    def adicionar_procedimento(self, cd_procedimento_interno: str, qt_solicitada: str, qt_autorizada: str) -> None:
        """
        Atualizar os procedimentos da autorização no Tasy.
        :param cd_procedimento_interno: Código do procedimento interno;
        :param qt_solicitada: Quantidade solicitada;
        :param qt_autorizada: Quantidade autorizada;
        """
        # Clica no botão adicionar
        if not self.bot.element_click(xpath="//*[contains(text(), 'Adicionar')]"):
            mensagem_erro = f"Botão (Adicionar) não localizado."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        # Insere o procedimento interno no campo 'Procedimento'
        xpath = "//input[@name='NR_SEQ_PROC_INTERNO']"
        self.bot.element_set_text(xpath=xpath, text=cd_procedimento_interno, delay=1000)
    
        # Espera o Tasy reconhecer o medicamento
        nome_procedimento = ""
        for n in range(20):
            xpath = "//*[contains(@w-model,'NR_SEQ_PROC_INTERNO')]/div/div/div/input"
            nome_procedimento = self.bot.element_get_value(xpath=xpath, tentativas=1)
            if nome_procedimento != "":
                break
            self.bot.wait(500)
        if nome_procedimento == "":
            mensagem_erro = f"Procedimento não reconhecido pelo Tasy."
            raise Exception([LOG_EX_NEGOCIO, mensagem_erro])
    
        # Preenche o campo 'Quantidade solicitada'
        self.bot.find_element("//input[@name='QT_SOLICITADA']", By.XPATH).clear()
        self.bot.find_element("//input[@name='QT_SOLICITADA']", By.XPATH).send_keys(qt_solicitada)
    
        # Se aparecer o popup informando que o procedimento não requer autorização do convênio, clica no botão 'OK'
        xpath = "//div[contains(text(),'autorização do convênio')]"
        if self.bot.find_element(xpath, By.XPATH, waiting_time=2000):
            self.bot.element_click(xpath="//button[contains(text(),'Ok')]", delay=500)
    
        # Preenche o campo 'Quantidade autorizada'
        self.bot.find_element("//input[@name='QT_AUTORIZADA']", By.XPATH).clear()
        self.bot.find_element("//input[@name='QT_AUTORIZADA']", By.XPATH).send_keys(qt_autorizada)
    
        # Clica em 'Salvar'
        xpath = "//div[contains(@class, 'enable') and div[div[span[text() = 'Salvar']]]]"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
    
        # Confirma a alteração
        xpath = f"//div[div[div[span[text() = '{cd_procedimento_interno}' or text() = '']]]]/div/div/span[text()='{qt_autorizada}']"
        if not self.bot.find_element(xpath, By.XPATH):
            mensagem_erro = f"Timeout ao confirmar a adição do procedimento."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        # Se não houver essa espera o Tasy apresenta falha ao salvar
        self.bot.wait(4000)
    
    def atualizar_materiais(self):
        """
        Atualizar a coluna 'Quantidade autorizada' com o valor da coluna 'Quantidade Solicitada' na aba 'Materiais'
        da autorização no Tasy.
        """
        # Clicar na aba 'Materiais'
        self.bot.find_element("//div[span[text() = 'Materiais']]", By.XPATH, ensure_clickable=True).click()
    
        # Espera a tela carregar
        xpath = "//span[text() = 'Material TUSS']"
        if not self.bot.search_element(xpath=xpath, tentativas=10):
            raise Exception([LOG_EX_SISTEMA, "Tela de materiais não localizada."])
    
        # Aumenta o número de autorizações que são visualizadas na tabela. Ele pode n existir, por isso não tem raise.
        xpath = "//tasy-listbox[contains(@class, 'ng-isolate-scope')]"
        if self.bot.element_click(xpath=xpath, tentativas=2):
            xpath = "//a[span[text() = 'Todos']]"
            if not self.bot.element_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, "Opção (Todos) não localizada."])
    
        # Pegar a quantidade de linhas da tabela de materiais
        xpath = "//i[@id = 'totalRecordsPageFinish']"
        qt_linhas = int(self.bot.element_get_text(xpath=xpath, tentativas=6))
    
        for linha in range(qt_linhas):
            # Pega a quantidade solicitada
            xpath = f"//div[div[div[div[div[span[text() = 'Material TUSS']]]]]]/div[5]/div[3]/div/" \
                    f"div[@data-row-idx='{linha}']/div[3]/div/span"
            qt_solicitada = self.bot.element_get_text(xpath=xpath, tentativas=6)
    
            # Pega a quantidade autorizada
            xpath = f"//div[div[div[div[div[span[text() = 'Material TUSS']]]]]]/div[5]/div[3]/div/" \
                    f"div[@data-row-idx='{linha}']/div[4]/div/span"
            qt_autorizada = self.bot.element_get_text(xpath=xpath, tentativas=6)
    
            if qt_solicitada != qt_autorizada:
                # Clica na linha do material
                xpath = f"//div[div[div[div[div[span[text() = 'Material TUSS']]]]]]/div[5]/div[3]/div/" \
                        f"div[@data-row-idx='{linha}']"
                if not self.bot.element_left_click(xpath=xpath):
                    raise Exception([LOG_EX_SISTEMA, f"Linha do material não localizada."])
    
                # Clica no desenho de um lapis no fim da linha do material selecionado
                if not self.bot.element_left_click(xpath="//a[@id='_inlineEdit']"):
                    raise Exception(
                        [LOG_EX_SISTEMA, f"Botão para editar o material não localizado."])
    
                # Preenche o campo 'Quantidade autorizada' com a quantidade solicitada
                xpath = "//input[@name='QT_AUTORIZADA']"
                self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).clear()
                self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(qt_solicitada)
    
                # Clica em 'Salvar'
                self.bot.find_element("(//button[text() = 'Salvar'])[2]", By.XPATH, ensure_clickable=True).click()
                self.bot.wait(1000)
    
                # Espera a página concluir o processamento
                xpath = f"//div[div[div[div[div[span[text() = 'Material TUSS']]]]]]/div[5]/div[3]/div/" \
                        f"div[@data-row-idx='{linha}']/div[4]/div/span"
                for i in range(60):
                    qt_autorizada = self.bot.element_get_text(xpath=xpath, tentativas=2)
                    if qt_autorizada == qt_solicitada:
                        break
                    self.bot.wait(500)
                if qt_autorizada != qt_solicitada:
                    raise Exception([LOG_EX_SISTEMA, f"Timeout ao confirmar a atualização."])
    
    def anexar_arquivo(self, tipo_anexo: str, dir_arquivo: str):
        """
        Realizar upload de arquivos para a aba 'Anexos' da autorização no Tasy.
        :param tipo_anexo: Tipo do anexo;
        :param dir_arquivo: Diretório dos arquivos que serão anexados no Tasy.
        """
        # Clicar na aba 'Anexos'
        if not self.bot.element_click(xpath="//div[span[text() = 'Anexos']]", delay=1000):
            raise Exception([LOG_EX_SISTEMA, "Aba (Anexos) não localizada."])
    
        # Espera a tela carregar
        xpath = "//span[text() = 'Arquivo']"
        if not self.bot.find_element(xpath, By.XPATH, ensure_visible=True):
            raise Exception([LOG_EX_SISTEMA, "Tela de anexos não localizada."])
    
        # Pegar a quantidade de arquivos antes de realizar o upload
        xpath = "(//i[@id = 'totalRecordsPageFinish'])[2]"
        qt_arquivos_antes = int(self.bot.find_element(xpath, By.XPATH, ensure_visible=True).text)
    
        # Clica no botão 'Adicionar'
        if not self.bot.element_click("//*[contains(text(), 'Adicionar')]"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])
    
        # Seleciona o 'Tipo de anexo'
        self.bot.element_click("//div[input[@name='NR_SEQ_TIPO']]")
        if not self.bot.element_click(f"//a[span[contains(text(),'{tipo_anexo}')]]"):
            raise Exception([LOG_EX_NEGOCIO, f"Tipo de anexo ({tipo_anexo}) não localizado."])
    
        self.bot.upload_arquivo_background(
            xpath_upload="//*[@id='DS_ARQUIVO']", caminho_arquivo=dir_arquivo,
            xpath_confirmacao="//div[contains(text(),'Remover')]"
        )
    
        # Clica em 'Salvar'
        xpath = "//div[contains(@class, 'enable') and div[div[span[text() = 'Salvar']]]]"
        self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
    
        # Espera a página concluir o processamento
        qt_arquivos_depois = 0
        xpath = "(//i[@id = 'totalRecordsPageFinish'])[2]"
        for i in range(60):
            n = self.bot.find_element(xpath, By.XPATH).text
            qt_arquivos_depois = int(n) if n != '' else 0
            if qt_arquivos_depois > qt_arquivos_antes:
                break
            self.bot.wait(500)
        if not qt_arquivos_depois > qt_arquivos_antes:
            raise Exception([LOG_EX_SISTEMA, "Timeout ao confirmar o upload do anexo."])
    
    def adicionar_autorizacao(self, convenio: str, medico_solicitante: str, data_prevista: str = '', 
                              tipo_autorizacao: str = '', procedimento: str = '', dias_autorizados: str = '',
                              observacao: str = '', indicacao_clinica: str = '') -> str:
        """
        Adicionar nova autorização no Tasy.
        :param convenio: Convênio;
        :param data_prevista: Data prevista;
        :param medico_solicitante: Médico solicitante;
        :param tipo_autorizacao: Tipo de autorização;
        :param procedimento: Procedimento interno;
        :param dias_autorizados: Dias autorizados;
        :param observacao: Observação;
        :param indicacao_clinica: Indicação clínica.
        :return: Sequência da nova autorização.
        """
        # Desmarca o checkbox da linha que estiver selecionada, se houver
        self.bot.element_click(xpath="//*[contains(@class,'cell-checkbox frozen')]", tentativas=6, delay=1000)
    
        # Clica no botão 'Adicionar'
        if not self.bot.element_click(xpath="//*[contains(text(), 'Adicionar')]", delay=1000):
            raise Exception([LOG_EX_SISTEMA, "Botão (Adicionar) não localizado."])
    
        # Pega o valor do campo 'Sequência'
        autorizacao = self.bot.element_get_value("//*[@name= 'NR_SEQUENCIA']")
        if autorizacao == '':
            raise Exception([LOG_EX_SISTEMA, "Tela de edição da nova autorização não localizada."])
    
        # Preenche o campo 'Tipo de autorização'
        if tipo_autorizacao != '':
            self.bot.element_click(xpath="//div[input[@name='IE_TIPO_AUTORIZACAO']]", delay=1000)
            if not self.bot.element_click(xpath=f"//a[span[text()='{tipo_autorizacao}']]", delay=250):
                mensagem_erro = f"Tipo de autorização ({tipo_autorizacao}) não localizado."
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro])
    
        # Preenche o campo 'Convênio'
        self.bot.element_click("//div[input[@name='CD_CONVENIO']]")
        if not self.bot.element_click(xpath=f"//a[span[text()='{convenio}']]", delay=250):
            raise Exception([LOG_EX_NEGOCIO, f"Convênio ({convenio}) não localizado."])
    
        # Preenche o campo 'Data prevista'
        if data_prevista != '':
            self.bot.element_set_text("//*[@name= 'DT_ENTRADA_PREVISTA']", data_prevista)
    
        # Preenche o campo 'Médico solicitante'
        self.bot.element_set_text("//*[@name= 'CD_MEDICO_SOLICITANTE']", medico_solicitante)
        self.bot.tab()
        nm_medico = ''
        for n in range(20):
            nm_medico = self.bot.element_get_value("//input[@name='txDescription']")
            if nm_medico != '':
                break
            self.bot.wait(500)
        if nm_medico == '':
            mensagem_erro = f"Médico solicitante ({medico_solicitante}) não localizado."
            raise Exception([LOG_EX_NEGOCIO, mensagem_erro])
    
        # Preenche o campo 'Procedimento'
        if procedimento != '':
            # Clica no campo 'Procedimento' para abrir uma tela de pesquisa
            self.bot.element_click("//div[div[span='Procedimento']]//input[@class='has-locator input-open-locator']")
            # Na tela de pesquisa, insere o procedimento no campo 'Código interno'
            self.bot.element_set_text("//input[@name='NR_SEQ_PROC_INTERNO']", procedimento, delay=1000)
            # Clica em 'Filtrar'
            self.bot.element_click("//button[contains(text(),'Filtrar')]")
            # Espera o procedimento aparecer na tabela de resultados
            if not self.bot.search_element(f"//div[span[text()='{procedimento}']]"):
                raise Exception([LOG_EX_NEGOCIO, f"Procedimento ({procedimento}) não localizado."])
            self.bot.element_click("//button[span[text()='Ok']]")
            # Espera o Tasy trazer a descrição do medicamento
            ds_procedimento = ''
            for n in range(20):
                ds_procedimento = self.bot.element_get_value("//input[@name='DS_PROCEDIMENTO']")
                if ds_procedimento != '':
                    break
                self.bot.wait(500)
            if ds_procedimento == '':
                raise Exception([LOG_EX_NEGOCIO, f"Procedimento ({procedimento}) não localizado."])
    
        # Preenche o campo 'Dias autorizados'
        if dias_autorizados != '':
            self.bot.element_set_text("//*[@name= 'QT_DIA_AUTORIZADO']", dias_autorizados)
    
        # Preenche o campo 'Observação'
        if observacao != '':
            self.bot.element_set_text("//*[@name= 'DS_OBSERVACAO']", observacao)
    
        # Preenche o campo 'Indicação clínica'
        if indicacao_clinica != '':
            self.bot.find_element(selector="//*[@name= 'DS_INDICACAO']", by=By.XPATH).send_keys(indicacao_clinica)
    
        # Clica no botão 'Salvar'
        if not self.bot.element_click("//*[@text = 'Salvar']"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Salvar) não localizado."])
    
        # Verifica se salvou com sucesso
        if not self.bot.search_element(xpath=f"//span[text() = '{autorizacao}']", tentativas=60):
            mensagem_erro = "Não foi possível confirmar a adição da nova autorização."
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])
    
        return autorizacao
    
    def vincular_atendimento(self, autorizacao: str, atendimento: str):
        """
        Vincular atendimento a autorização.
        :param autorizacao: Sequência da autorização;
        :param atendimento: Número do atendimento.
        """
        # Clica com o botão direito do mouse na linha referente a autorização da tabela de autorizações
        if not self.bot.element_right_click(f"//div[div[div[span[text() = '{autorizacao}']]]]"):
            raise Exception([LOG_EX_SISTEMA, "Autorização não localizada."])
    
        # Clica no item "Vincular -> Atendimento" da lista suspensa
        self.bot.element_click("//*[text()='Vincular']")
        if not self.bot.element_click("//div[text()='Atendimento']"):
            raise Exception([LOG_EX_SISTEMA, "Menu (Vincular -> Atendimento) não localizado."])
    
        # Alterar a quantidade de linhas por página para 'Todas' se houver várias páginas
        xpath = "//div[div[div[div[span[text()='Vincular atendimento']]]]]//div[div[a[*[*[text()='---']]]]]"
        if self.bot.element_click(xpath=xpath, tentativas=6, delay=1000):
            self.bot.element_click(xpath="//span[text()='Todos']", tentativas=2, delay=1000)
            self.bot.wait(2000)
            self.bot.type_keys(keys=[Keys.SHIFT, Keys.TAB, Keys.TAB])
        else:
            self.bot.type_keys(keys=[Keys.SHIFT, Keys.TAB])
    
        # É necessário usar o 'Page Down' para os atendimentos carregarem
        xpath = f"//div[div[div[div[span[text()='Vincular atendimento']]]]]//div[div[div[span[text() = '{atendimento}']]]]"
        for n in range(10):
            if self.bot.find_element(xpath, By.XPATH, 1000):
                break
            self.bot.page_down()
        if not self.bot.find_element(xpath, By.XPATH):
            raise Exception([LOG_EX_SISTEMA, "Atendimento não localizada."])
    
        # Seleciona o atendimento e clica em "OK"
        self.bot.find_element(xpath, By.XPATH).click()
        self.bot.element_click("//button[span[contains(text(),'OK')]]")
    
        # Verifica se salvou com sucesso
        xpath = f"//div[div[div[span[text() = '{autorizacao}']]] and div[div[span[text() = '{atendimento}']]]]"
        if self.bot.search_element(xpath=xpath):
            return
    
        raise Exception([LOG_EX_SISTEMA, "Não foi possível confirmar o vínculo do atendimento."])

    def acessar_autorizacao(self, autorizacao: str):
        """
        Realiza um duplo click na linha da autorização.
        :param autorizacao: Sequência da autorização.
        """
        # Seleciona a autorização na tabela de autorizações
        if not self.bot.element_double_click(f"//div[div[div[span[text() = '{autorizacao}']]]]", delay=1000):
            raise Exception([LOG_EX_SISTEMA, "Autorização não localizada."])
    
        # Espera a tela carregar
        if not self.bot.search_element("//div[contains(text(), 'Autorização procedimento')]"):
            raise Exception([LOG_EX_SISTEMA, "Tela com dados da autorização não localizada."])
    
    def retornar_tabela_autorizacoes(self) -> None:
        """
        Clica no botão 'Guia' para retornar para a tela de autorizações.
        """
        # Clica em 'Guia' no canto superior esquerdo da tela
        self.bot.find_element("//div[div[text() = 'Guia']]", By.XPATH, ensure_clickable=True).click()
    
        # Espera a tela carregar
        if not self.bot.search_element(xpath="//div[contains(text(), 'Autorizações')]"):
            raise Exception([LOG_EX_SISTEMA, "Tela de autorizações não localizada."])
    
    def limpar_filtro_autorizacao(self):
        """
        Função que limpa o filtro de autorizações
        """
        if not self.bot.element_click(xpath="//button[text()='Ações do filtro']"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Ações do filtro) não encontrado."])
    
        if not self.bot.element_click(xpath="//div[text()='Limpar filtros']"):
            raise Exception([LOG_EX_SISTEMA, "Botão (Limpar filtros) não encontrado."])
