from config import RPA_DIR_DOWNLOADS, TASY_URL, TASY_USER, TASY_PWD, LOG_EX_SISTEMA, LOG_EX_NEGOCIO, HEADLESS
from oncopackages.pastas_arquivos.pastas_arquivos import esperar_conclusao_download
from selenium.webdriver.common.action_chains import ActionChains
from oncopackages.ferramentas.browser import Browser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from banco_dados_tasy import BancoDadosTasy
from banco_dados_rpa import BancoDadosRpa
from selenium import webdriver
import urllib.parse
import glob
import time
import os


class Tasy:
    def __init__(self, bd_rpa: BancoDadosRpa, bd_tasy: BancoDadosTasy = None):
        # Configuração do browser
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        if HEADLESS:  # Define se o navegador vai ficar visível ou não
            options.add_argument('--headless')
        prefs = {"download.default_directory": RPA_DIR_DOWNLOADS}  # Define a pasta usada para salvar os downloads
        options.add_experimental_option('prefs', prefs)
        self._options = options

        self.browser: Browser
        self.bd_rpa = bd_rpa
        self.bd_tasy = bd_tasy

    def login(self):
        """
        Realiza o login no Tasy.
        """
        mensagem_erro = "Falha ao realizar login no Tasy. "
        try:
            # Abre o navegador e acessa o Tasy
            self.browser = Browser(driver=webdriver.Chrome(options=self._options))
            self.browser.get(TASY_URL)

            # Informa o usuário
            self.browser.search_element("loginUsername", By.ID, waiting_time=30).send_keys(TASY_USER)

            # Informa o senha
            self.browser.search_element("loginPassword", By.ID).send_keys(TASY_PWD)

            # Entrar
            self.browser.search_element("loginPassword", By.ID).send_keys(Keys.ENTER)

            # Verificar se o login foi realizado com sucesso
            if self.browser.search_element("//a[text() = 'Funções']", By.XPATH, waiting_time=60):
                return

            # Verificar se a senha está errada
            if self.browser.search_element(By.XPATH, "//*[contains(text(), 'Usuário ou senha inválido.')]", waiting_time=0):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Usuário ou senha inválido."])

            # Reportar falha genérica
            raise Exception([LOG_EX_SISTEMA, mensagem_erro])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)

    def trocar_estabelecimento(self, estabelecimento: str):
        """
        Verifica se o Tasy já se encontra no estabelecimento desejado e troca caso necessário.
        :param estabelecimento: Estabelecimento que deseja acessar.
        """
        mensagem_erro = 'Falha ao trocar o estabelecimento. '
        try:
            # Verificar se já está no estabelecimento correto
            xpath = "//*[@class='w-footer__establishment']"  # Nome do estab que fica no canto inferior central de qualquer tela
            estab_atual = self.browser.search_element(By.XPATH, xpath).get_attribute('innerText')
            estab_atual = estab_atual.replace(" ", "")
            estab_necessario = estabelecimento.replace(" ", "")
            if estab_atual == estab_necessario:
                # Verificar se o popup de seleção do estabelecimento está ativo
                if self.browser.search_element(By.XPATH, "//div[contains(text(), 'Trocar estabelecimento')]", 2):
                    # Clicar em 'Cancelar'
                    self.browser.search_element(By.XPATH, "//button[contains(text(), 'Cancelar')]").click()
                return

            # Verificar se o popup de seleção do estabelecimento está ativo
            if not self.browser.search_element("//div[contains(text(), 'Trocar estabelecimento')]", By.XPATH, 1):
                # Ao dar refresh na página o popup vai aparecer
                self.browser.refresh()

            # Abrir a lista suspensa
            self.browser.search_element(By.XPATH, "//div[input[@name='CD_ESTABELECIMENTO']]").click()

            # Clicar no item da lista suspensa desejado
            xpath = f"//a/span[text()='{estabelecimento}']"
            if not self.browser.element_click(By.XPATH, xpath, 10, 1):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f'Estabelecimento ({estabelecimento}) não localizado.'])

            # Clicar em 'Ok'
            self.browser.search_element(By.XPATH, "//button[contains(text(), 'Ok')]").click()

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
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
            if self.browser.search_element(By.XPATH, xpath, waiting_time=2):
                return

            # Clica no seta da direita da tela de funções
            if clicar_seta_direita:
                self.browser.search_element(By.XPATH, "//button[@class='w-apps__next']").click()

            # Clica no seta da esquerda da tela de funções
            if clicar_seta_esquerda:
                self.browser.search_element(By.XPATH, "//button[@class='w-apps__prev']").click()

            # Clicar na função
            if not self.browser.element_click(By.XPATH, f"//a/span[contains(text(), '{tasy_funcao}')]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Função ({tasy_funcao}) não localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)

    def fechar_funcao(self, nome_funcao: str) -> None:
        """
        Fecha a função do Tasy especificada.
        :param nome_funcao: Nome da função que deseja fechar.
        """
        mensagem_erro = "Falha ao fechar função do tasy. "
        try:
            # Clica em fechar a função
            if not self.browser.element_click(By.XPATH, f"//div[span[text()='{nome_funcao}']]/button"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Função ({nome_funcao}) não localizado."])

            # Aguarda a tela carregar
            if not self.browser.search_element(By.LINK_TEXT, "Funções"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Função ({nome_funcao}) não encerrada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)

    def download_arquivo(self, url_arquivo: str, timeout: int = 30) -> str:
        """
        Realiza o download de qualquer arquivo armazenado no Tasy.
        :param url_arquivo: Link do arquivo encontrado no banco de dados do Tasy.
        :param timeout: tempo máximo de espera pela conclusão do download (Em segundos).
        :return: Diretório completo do arquivo baixado.
        """
        mensagem_erro = f"Falha ao baixar o arquivo do Tasy."
        try:
            # Pega o nome do arquivo que será baixado
            nome_arquivo = url_arquivo.split('?')[url_arquivo.count('?')]

            # Conta a quantidade de arquivos na pasta de downloads com a mesma extensão do arquivo que será baixado
            extensao_arquivo = nome_arquivo.split('.')[nome_arquivo.count('.')]
            arquivos = glob.glob(os.path.join(RPA_DIR_DOWNLOADS, f'*.{extensao_arquivo}'))
            qt_arquivos_antes = len(arquivos)

            # Merge da URL do Tasy com o link do arquivo para gerar o link de download
            url_arquivo = urllib.parse.quote(url_arquivo, safe='()%').replace('/', '%2F')
            link_download = f"{TASY_URL}/TasyAppServer/resources/files?file={url_arquivo}"

            # Realiza o download abrindo o link criado
            self.browser.get(link_download)

            # Espera a conclusão do download por até timeout segundos
            qt_arquivos_apos = 0
            for i in range(timeout):
                arquivos = glob.glob(os.path.join(RPA_DIR_DOWNLOADS, f'*.{extensao_arquivo}'))
                qt_arquivos_apos = len(arquivos)
                if qt_arquivos_apos > qt_arquivos_antes:
                    break
                time.sleep(1)

            if qt_arquivos_apos <= qt_arquivos_antes:
                raise Exception([LOG_EX_SISTEMA, f'Timeout ao baixar o arquivo ({nome_arquivo}) do Tasy.'])

            # Pega o diretório completo do arquivo baixado
            files_path = glob.glob(os.path.expanduser(os.path.join(RPA_DIR_DOWNLOADS, f"*{extensao_arquivo}")))
            dir_arquivo = max(files_path, key=os.path.getctime)

            return dir_arquivo

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            self.browser.get(TASY_URL)
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
            self.browser.element_click(By.XPATH, "//button[span[text()='Relatórios']]", delay=1)
            if not self.browser.element_click(By.XPATH, "//div[text()='Configurações']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Menu (Relatórios -> Configurações) não localizado."])

            # Preenche o campo 'Código'
            if not self.browser.element_set_text(By.XPATH, "//input[@name='CD_RELATORIO']", text=codigo_relatorio, delay=1):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de pesquisa não localizada."])

            # Clica em 'Filtrar'
            if not self.browser.element_click(By.XPATH, "//button[contains(text(),'Filtrar')]", delay=1):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Filtrar) não localizado."])

            # Clica na linha referente ao CATE pesquisado
            if not self.browser.element_click(By.XPATH, f"//div[div[div[span[text()='{codigo_relatorio}']]]]", delay=1):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + f"Relatório ({codigo_relatorio}) não localizado."])

            # Clica em 'Visualizar'
            if not self.browser.element_click(By.XPATH, "//button[span[text()='Visualizar']]", delay=1):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Visualizar) não localizado."])

            # Esperar o download ser concluído
            arquivo_baixado = esperar_conclusao_download(timeout=60)

            # Clica em 'Cancelar'
            if not self.browser.element_click(By.XPATH, "//button[span[text()='Cancelar']]"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Cancelar) não localizado."])

            return arquivo_baixado

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
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
            if not self.browser.search_element(xpath, By.XPATH):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Localizar paciente) não localizado."])

            # Se não for a primeira pesquisa, realizar o filtro a partir do campo 'Código' da barra superior.
            consulta_realizada = False
            xpath = "//a[@class='btn inline-edit-link ng-scope']"
            if self.browser.search_element(By.XPATH, xpath, waiting_time=2):
                # Clica no desenho do lapis para editar o campo 'Código'
                action = ActionChains(self.browser.driver)
                elemento = self.browser.find_element(By.XPATH, xpath)
                action.click(elemento).perform()

                # Insere o prontuário e tecla 'Enter' para pesquisar
                xpath = "//div[span[text()='Código']]/div/span/input"
                if self.browser.search_element(By.XPATH, xpath, waiting_time=2):
                    self.browser.search_element(By.XPATH, xpath).send_keys(prontuario)
                    self.browser.search_element(By.XPATH, xpath).send_keys(Keys.ENTER)
                    consulta_realizada = True

            # Se for a primeira pesquisa ou não for possível realizar a pesquisa pelo método anterior,
            # realizar o filtro a partir do botão com o símbolo da lupa.
            if consulta_realizada is False:
                # Clicar no ícone de Pesquisar que fica no canto superior esquerdo
                if not self.browser.element_click(By.XPATH, "//div[div[@class='person-icon-finder']]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Ícone de pesquisa (Lupa) não localizado."])

                # Ativa a aba 'Pessoa'
                if not self.browser.element_click(By.XPATH, "//div[span[text()='Pessoa']]", delay=1):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Aba (Pessoa) não localizada."])

                # Insere o número do prontuário no campo de pesquisa
                xpath = "//input[contains(@name, 'CD_PESSOA_FISICA_')]"
                if not self.browser.element_set_text(By.XPATH, xpath, prontuario, delay=1):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Campo (Código) não localizado."])

                # Clica no botão Filtrar
                if not self.browser.element_click(By.XPATH, "//button[contains(text(),'Filtrar')]", delay=1):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Filtrar) não localizado."])

                # Espera o prontuário aparecer na tabela de resultados
                if not self.browser.element_displayed(By.XPATH, f"//div[div/div/span[text()='{prontuario}']]"):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Prontuario não localizado."])

                # Clica no botão 'Ok'
                if not self.browser.element_click(By.XPATH, "//button[span[text() = 'Ok']]"):
                    raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão (Ok) não localizado."])

                if fechar_ccp:
                    # Espera a tela da função "Cadastro Completo de Pessoa" carregar
                    if not self.browser.element_displayed(By.XPATH, "//*[text() = 'Todos complementos']"):
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de resultado da pesquisa não localizada."])

                    # Clica no botão 'Ok' caso apareça algum popup com o título 'Informação'
                    self.browser.element_click(By.XPATH, "//button[text() = 'Ok']", 4)

                    # Fecha a função 'Cadastro Completo de Pessoa'
                    xpath = "//div[span[text()='Cadastro Completo de Pessoas']]/button"
                    if not self.browser.element_click(By.XPATH, xpath):
                        mensagem_erro += "Não foi possível encerrar a função (Cadastro Completo de Pessoa)."
                        raise Exception([LOG_EX_SISTEMA, mensagem_erro])

            # Fechar qualquer popup de alerta que aparecer. Pode aparecer mais de 1
            for i in range(10):
                self.browser.type_keys(Keys.ESCAPE)

            # Verifica se a pesquisa retornou o prontuário desejado
            if not self.browser.element_displayed(By.XPATH, f"//span[@id='NR_PRONTUARIO']/span[text()='{prontuario}']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela de resultado da pesquisa não localizada."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
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
            if not self.browser.search_element(By.XPATH, xpath, waiting_time=30):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Botão Pesquisar não localizado."])

            # Se não for a primeira pesquisa, realizar o filtro a partir do campo atendimento da barra superior.
            consulta_realizada = False
            xpath = "//a[@class='btn inline-edit-link ng-scope']"
            if self.browser.search_element(By.XPATH, xpath, waiting_time=2000):
                # Clica no desenho do lapis para editar o campo do atendimento
                action = ActionChains(self.browser.driver)
                elemento = self.browser.search_element(By.XPATH, xpath)
                action.click(elemento).perform()
                # Insere o atendimento:
                try:
                    xpath = "//div[span[text()='Atendimento']]/div/span/input"
                    self.browser.search_element(By.XPATH, xpath).send_keys(nr_atendimento)
                    self.browser.type_keys(Keys.ENTER)
                    consulta_realizada = True
                except:
                    consulta_realizada = False

            # Se for a primeira pesquisa ou não for possível realizar a pesquisa pelo método anterior,
            # realizar o filtro a partir do botão com o símbolo da lupa.
            xpath = "//a[@class='btn inline-edit-link ng-scope']"
            if not self.browser.search_element(By.XPATH, xpath, waiting_time=1) or consulta_realizada is False:
                # Clicar no ícone de Pesquisar que fica no canto superior esquerdo
                xpath = "//div[div[@class='person-icon-finder']]"
                self.browser.search_element(By.XPATH, xpath).click()

                # Insere o número do atendimento no campo de pesquisa
                xpath = "//input[@name='NR_ATENDIMENTO']"
                self.browser.search_element(By.XPATH, xpath).clear()
                self.browser.search_element(By.XPATH, xpath).send_keys(nr_atendimento)

                # Clica no botão Filtrar
                self.browser.search_element("//button[contains(text(),'Filtrar')]", By.XPATH).click()

                # Duplo click na primeira linha da tabela de resultados
                if not self.browser.element_double_click(By.XPATH, f"//div[div/div/span[text()='{nr_atendimento}']]"):
                    raise Exception([LOG_EX_NEGOCIO, mensagem_erro + f"Atendimento ({nr_atendimento}) não localizado."])

            # Esperar a tela do PEPA carregar
            if not self.browser.element_displayed(By.XPATH, "//span[text()='Agenda de consulta']"):
                raise Exception([LOG_EX_SISTEMA, mensagem_erro + "Tela do prontuário do paciente não localizada."])

            # Fechar qualquer popup de alerta que aparecer. Pode aparecer mais de 1
            for i in range(8):
                self.browser.type_keys(Keys.ESCAPE, 1)

            # Verifica se a tela carregou
            if not self.browser.search_element(By.XPATH, "//div[text() = 'Paciente']", waiting_time=2):
                raise Exception([LOG_EX_NEGOCIO, mensagem_erro + "Popup de erro localizado após pesquisa."])

        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro, self.browser)
            raise ValueError(error_message)

