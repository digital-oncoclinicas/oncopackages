from config import RPA_DIR_DOWNLOADS, TASY_URL, TASY_USER, TASY_PWD, LOG_EX_SISTEMA, LOG_EX_NEGOCIO
from oncopackages.ferramentas.web_bot import Webbot
from botcity.web.bot import ActionChains, By
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
import urllib.parse


class Tasy:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        self.bot = Webbot()
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self):
        """
        Realiza o login no Tasy.
        """
        mensagem_erro = "Falha ao realizar login no Tasy. "
        try:
            # Abre o navegador e acessa o Tasy
            self.bot.navigate_to(TASY_URL)

            # Navegador em tela cheia
            self.bot.maximize_window()

            # Informa o usuário
            self.bot.find_element("loginUsername", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(TASY_USER)

            # Informa o senha
            self.bot.find_element("loginPassword", By.ID).send_keys(TASY_PWD)

            # Entrar
            self.bot.enter()

            # Verificar se o login foi realizado com sucesso
            if self.bot.find_element("//a[text() = 'Funções']", By.XPATH, waiting_time=60000):
                return

            # Verificar se a senha está errada
            if self.bot.find_element("//*[contains(text(), 'Usuário ou senha inválido.')]", By.XPATH, waiting_time=0):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Usuário ou senha inválido."])

            # Reportar falha genérica
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def trocar_estabelecimento(self, estabelecimento: str):
        """
        Verifica se o Tasy já se encontra no estabelecimento desejado e troca caso necessário.
        :param estabelecimento: Estabelecimento que deseja acessar.
        """
        mensagem_erro = 'Falha ao trocar o estabelecimento. '
        try:
            # Verificar se já está no estabelecimento correto
            # Nome do estabelecimento que fica no canto inferior central de qualquer tela
            xpath = "//*[@class='w-footer__establishment']"
            estab_atual = self.bot.find_element(xpath, By.XPATH, ensure_visible=True).get_attribute('innerText')
            estab_atual = estab_atual.replace(" ", "")
            estab_necessario = estabelecimento.replace(" ", "")
            if estab_atual == estab_necessario:
                # Verificar se o popup de seleção do estabelecimento está ativo
                if self.bot.find_element("//div[contains(text(), 'Trocar estabelecimento')]", By.XPATH, waiting_time=2000):
                    # Clicar em 'Cancelar'
                    self.bot.find_element("//button[contains(text(), 'Cancelar')]", By.XPATH, ensure_clickable=True).click()
                return

            # Verificar se o popup de seleção do estabelecimento está ativo
            if not self.bot.find_element("//div[contains(text(), 'Trocar estabelecimento')]", By.XPATH, waiting_time=0):
                # Ao dar refresh na página o popup vai aparecer
                self.bot.refresh()

            # Abrir a lista suspensa
            self.bot.find_element("//div[input[@name='CD_ESTABELECIMENTO']]", By.XPATH, ensure_clickable=True).click()

            # Clicar no item da lista suspensa desejado
            xpath = f"//a/span[text()='{estabelecimento}']"
            if not self.bot.element_click(xpath, tentativas=10, delay=500):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f'Estabelecimento ({estabelecimento}) não localizado.'])

            # Clicar em 'Ok'
            self.bot.find_element("//button[contains(text(), 'Ok')]", By.XPATH).click()

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def executar_funcao(self, tasy_funcao: str, clicar_seta_direita: bool = False, clicar_seta_esquerda: bool = False):
        """
        Verifica se o Tasy já está com a função desejada em execução e à executa caso necessário.
        :param tasy_funcao: Função que deseja executar;
        :param clicar_seta_direita: Se True, clica no seta da direita a tela de funções do Tasy;
        :param clicar_seta_esquerda: Se True, clica no seta da esquerda a tela de funções do Tasy.
        """
        mensagem_erro = "Falha ao executar a função do tasy. "
        try:
            # Verificar se a função já está em execução
            xpath = f"//div/span[contains(text(), '{tasy_funcao}')]"
            if self.bot.find_element(xpath, By.XPATH, ensure_clickable=True, waiting_time=1000):
                return

            # Clica no seta da direita da tela de funções
            if clicar_seta_direita:
                xpath = "//button[@class='w-apps__next']"
                self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

            # Clica no seta da esquerda da tela de funções
            if clicar_seta_esquerda:
                xpath = "//button[@class='w-apps__prev']"
                self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

            # Clicar na função
            xpath = f"//a/span[contains(text(), '{tasy_funcao}')]"
            if not self.bot.element_click(xpath=xpath):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Função ({tasy_funcao}) não localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def fechar_funcao(self, nome_funcao: str) -> None:
        """
        Fecha a função do Tasy especificada.
        :param nome_funcao: Nome da função que deseja fechar.
        """
        mensagem_erro = "Falha ao fechar função do tasy. "
        try:
            # Clica em fechar a função
            if not self.bot.element_click(xpath=f"//div[span[text()='{nome_funcao}']]/button"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Função ({nome_funcao}) não localizado."])

            # Aguarda a tela carregar
            if not self.bot.find_element("Funções", By.LINK_TEXT, ensure_visible=True, ensure_clickable=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Função ({nome_funcao}) não encerrada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def download_arquivo(self, url_arquivo: str, timeout: int = 30000) -> str:
        """
        Realiza o download de qualquer arquivo armazenado no Tasy.
        :param url_arquivo: Link do arquivo encontrado no banco de dados do Tasy.
        :param timeout: tempo máximo de espera pela conclusão do download.
        :return: Diretório completo do arquivo baixado.
        """
        nome_arquivo = str()
        try:
            # Pega o nome do arquivo que será baixado
            nome_arquivo = url_arquivo.split('?')[url_arquivo.count('?')]

            # Conta a quantidade de arquivos na pasta de downloads com a mesma extensão do arquivo que será baixado
            extensao_arquivo = nome_arquivo.split('.')[nome_arquivo.count('.')]
            qt_arquivos_antes = self.bot.get_file_count(file_extension=extensao_arquivo)

            # Merge da URL do Tasy com o link do arquivo para gerar o link de download
            url_arquivo = urllib.parse.quote(url_arquivo, safe='()%').replace('/', '%2F')
            link_download = f"{TASY_URL}/TasyAppServer/resources/files?file={url_arquivo}"

            # Realiza o download abrindo o link criado
            self.bot.navigate_to(link_download)

            # Espera a conclusão do download por até timeout segundos
            qt_arquivos_apos = 0
            for i in range(int(timeout / 500)):
                qt_arquivos_apos = self.bot.get_file_count(file_extension=extensao_arquivo)
                if qt_arquivos_apos > qt_arquivos_antes:
                    break
                self.bot.wait(500)

            if qt_arquivos_apos <= qt_arquivos_antes:
                raise Exception([LOG_EX_SISTEMA, f'Timeout ao baixar o arquivo ({nome_arquivo}) do Tasy.'])

            # Pega o diretório completo do arquivo baixado
            dir_arquivo = self.bot.get_last_created_file(path=RPA_DIR_DOWNLOADS)

            return dir_arquivo

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(f"Falha ao baixar o arquivo ({nome_arquivo}) do Tasy.", self.bot)
            self.bot.navigate_to(TASY_URL)
            raise ValueError(error_message)

    def emitir_relatorio(self, codigo_relatorio: str) -> str:
        """
        Emite relatórios em várias funções do Tasy.
        :param codigo_relatorio: Código do relatório que deseja baixar.
        :return: Diretório completo do relatório baixado.
        """
        mensagem_erro = f"Falha ao gerar relatório {codigo_relatorio}. "

        try:
            # Clica no menu "Relatórios -> Configurações"
            self.bot.element_click(xpath="//button[span[text()='Relatórios']]", delay=500)
            if not self.bot.element_click(xpath="//div[text()='Configurações']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Menu (Relatórios -> Configurações) não localizado."])

            # Preenche o campo 'Código'
            if not self.bot.element_set_text(xpath="//input[@name='CD_RELATORIO']", text=codigo_relatorio, delay=500):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de pesquisa não localizada."])

            # Clica em 'Filtrar'
            if not self.bot.element_click(xpath="//button[contains(text(),'Filtrar')]", delay=500):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Filtrar) não localizado."])

            # Clica na linha referente ao CATE pesquisado
            if not self.bot.element_click(xpath=f"//div[div[div[span[text()='{codigo_relatorio}']]]]", delay=500):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Relatório ({codigo_relatorio}) não localizado."])

            # Clica em 'Visualizar'
            if not self.bot.element_click(xpath="//button[span[text()='Visualizar']]", delay=500):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Visualizar) não localizado."])

            # Esperar o download ser concluído
            arquivo_baixado = self.bot.esperar_conclusao_download(timeout=60000)

            # Clica em 'Cancelar'
            if not self.bot.element_click(xpath="//button[span[text()='Cancelar']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Cancelar) não localizado."])

            return arquivo_baixado

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)
        
    def pesquisar_prontuario(self, prontuario: str, fechar_ccp: bool = False):
        """
        Realiza a pesquisa pelo prontuário do paciênte.
        :param prontuario: Prontuário do paciente;
        :param fechar_ccp: Fechar a função Cadastro Completo de Pessoas? Em alguns perfis ela não é exibida!
        """
        mensagem_erro = f"Falha ao pesquisar pela prontuário. "
        try:
            # Espera o desenho da lupa que fica no canto superior esquerdo aparecer
            xpath = "//div[@class='person-icon-finder']"
            if not self.bot.find_element(xpath, By.XPATH):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Localizar paciente) não localizado."])

            # Se não for a primeira pesquisa, realizar o filtro a partir do campo 'Código' da barra superior.
            consulta_realizada = False
            xpath = "//a[@class='btn inline-edit-link ng-scope']"
            if self.bot.find_element(xpath, By.XPATH, waiting_time=2000):
                # Clica no desenho do lapis para editar o campo 'Código'
                action = ActionChains(self.bot.driver)
                elemento = self.bot.find_element(xpath, By.XPATH)
                action.click(elemento).perform()

                # Insere o prontuário e tecla 'Enter' para pesquisar
                xpath = "//div[span[text()='Código']]/div/span/input"
                if self.bot.find_element(xpath, By.XPATH, waiting_time=2000, ensure_visible=True):
                    self.bot.find_element(xpath, By.XPATH, ensure_visible=True).send_keys(prontuario)
                    self.bot.enter()
                    consulta_realizada = True

            # Se for a primeira pesquisa ou não for possível realizar a pesquisa pelo método anterior,
            # realizar o filtro a partir do botão com o símbolo da lupa.
            if consulta_realizada is False:
                # Clicar no ícone de Pesquisar que fica no canto superior esquerdo
                if not self.bot.element_click("//div[div[@class='person-icon-finder']]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Ícone de pesquisa (Lupa) não localizado."])

                # Ativa a aba 'Pessoa'
                if not self.bot.element_click("//div[span[text()='Pessoa']]", delay=1000):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Aba (Pessoa) não localizada."])

                # Insere o número do prontuário no campo de pesquisa
                if not self.bot.element_set_text("//input[contains(@name, 'CD_PESSOA_FISICA_')]", prontuario, delay=1000):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo (Código) não localizado."])

                # Clica no botão Filtrar
                if not self.bot.element_click(xpath="//button[contains(text(),'Filtrar')]", delay=500):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Filtrar) não localizado."])

                # Espera o prontuário aparecer na tabela de resultados
                if not self.bot.element_wait_displayed(f"//div[div/div/span[text()='{prontuario}']]"):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Prontuario não localizado."])

                # Clica no botão 'Ok'
                if not self.bot.element_click("//button[span[text() = 'Ok']]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Ok) não localizado."])

                if fechar_ccp:
                    # Espera a tela da função "Cadastro Completo de Pessoa" carregar
                    if not self.bot.element_wait_displayed("//*[text() = 'Todos complementos']"):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de resultado da pesquisa não localizada."])

                    # Clica no botão 'Ok' caso apareça algum popup com o título 'Informação'
                    self.bot.element_click("//button[text() = 'Ok']", tentativas=4)

                    # Fecha a função 'Cadastro Completo de Pessoa'
                    xpath = "//div[span[text()='Cadastro Completo de Pessoas']]/button"
                    if not self.bot.element_click(xpath=xpath):
                        mensagem_erro += "Não foi possível encerrar a função (Cadastro Completo de Pessoa)."
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro])

                    # Verificar se aparece o popup de 'Operação abortada'
                    if self.bot.element_wait_displayed(xpath="//*[text()='Operação abortada']", tentativas=4):
                        xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
                        mensagem_erro += self.bot.element_get_text(xpath=xpath)
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro])

            # Fechar qualquer popup de alerta que aparecer. Pode aparecer mais de 1
            for i in range(10):
                self.bot.key_esc(wait=1000)

            # Verifica se a pesquisa retornou o prontuário desejado
            if not self.bot.element_wait_displayed(f"//span[@id='NR_PRONTUARIO']/span[text()='{prontuario}']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de resultado da pesquisa não localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

    def pesquisar_atendimento(self, nr_atendimento: str):
        """
        Pesquisa pelo número do atendimento.
        :param nr_atendimento: Número do atendimento.
        """
        mensagem_erro = "Falha ao pesquisar pelo atendimento no PEPA. "
        try:
            # Espera a tela carregar
            xpath = "//span[text()='Agenda de consulta']"
            if not self.bot.find_element(xpath, By.XPATH, waiting_time=30000, ensure_clickable=True):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão Pesquisar não localizado."])

            # Se não for a primeira pesquisa, realizar o filtro a partir do campo atendimento da barra superior.
            consulta_realizada = False
            xpath = "//a[@class='btn inline-edit-link ng-scope']"
            if self.bot.find_element(xpath, By.XPATH, waiting_time=2000):
                # Clica no desenho do lapis para editar o campo do atendimento
                action = ActionChains(self.bot.driver)
                elemento = self.bot.find_element(xpath, By.XPATH)
                action.click(elemento).perform()
                # Insere o atendimento:
                try:
                    xpath = "//div[span[text()='Atendimento']]/div/span/input"
                    self.bot.find_element(xpath, By.XPATH, ensure_visible=True).send_keys(nr_atendimento)
                    self.bot.enter()
                    consulta_realizada = True
                except:
                    consulta_realizada = False

            # Se for a primeira pesquisa ou não for possível realizar a pesquisa pelo método anterior,
            # realizar o filtro a partir do botão com o símbolo da lupa.
            xpath = "//a[@class='btn inline-edit-link ng-scope']"
            if not self.bot.find_element(xpath, By.XPATH, waiting_time=0) or consulta_realizada is False:
                # Clicar no ícone de Pesquisar que fica no canto superior esquerdo
                xpath = "//div[div[@class='person-icon-finder']]"
                self.bot.find_element(xpath, By.XPATH).click()

                # Insere o número do atendimento no campo de pesquisa
                xpath = "//input[@name='NR_ATENDIMENTO']"
                self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).clear()
                self.bot.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(nr_atendimento)

                # Clica no botão Filtrar
                self.bot.find_element("//button[contains(text(),'Filtrar')]", By.XPATH, ensure_clickable=True).click()

                # Duplo click na primeira linha da tabela de resultados
                if not self.bot.element_double_click(xpath=f"//div[div/div/span[text()='{nr_atendimento}']]"):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Atendimento ({nr_atendimento}) não localizado."])

            # Esperar a tela do PEPA carregar
            if not self.bot.element_wait_displayed(xpath="//span[text()='Agenda de consulta']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela do prontuário do paciente não localizada."])

            # Fechar qualquer popup de alerta que aparecer. Pode aparecer mais de 1
            for i in range(8):
                self.bot.key_esc(wait=1000)

            # Verifica se a tela carregou
            if not self.bot.find_element("//div[text() = 'Paciente']", By.XPATH, ensure_visible=True, waiting_time=2000):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Popup de erro localizado após pesquisa."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.bot)
            raise ValueError(error_message)

