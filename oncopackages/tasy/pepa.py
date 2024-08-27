from onco_packages.pastas_arquivos.pastas_arquivos import esperar_conclusao_download
from onco_packages.banco_dados.rpa import salvar_log_erro
from botcity.web.bot import ActionChains
from botcity.web import WebBot, By
import sys


def pesquisar_atendimento(bot: WebBot, nr_atendimento: str):
    """
    Pesquisa pelo número do atendimento na função PEPA.
    :param bot: Objeto da BotCity;
    :param nr_atendimento: Número do atendimento.
    """
    mensagem_erro = "Falha ao pesquisar pelo atendimento no PEPA. "
    try:
        # Espera a tela carregar
        xpath = "//span[text()='Agenda de consulta']"
        if not bot.find_element(xpath, By.XPATH, waiting_time=30000, ensure_clickable=True):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão Pesquisar não localizado."])

        # Se não for a primeira pesquisa, realizar o filtro a partir do campo atendimento da barra superior.
        consulta_realizada = False
        xpath = "//a[@class='btn inline-edit-link ng-scope']"
        if bot.find_element(xpath, By.XPATH, waiting_time=2000):
            # Clica no desenho do lapis para editar o campo do atendimento
            action = ActionChains(bot.driver)
            elemento = bot.find_element(xpath, By.XPATH)
            action.click(elemento).perform()
            # Insere o atendimento:
            try:
                xpath = "//div[span[text()='Atendimento']]/div/span/input"
                bot.find_element(xpath, By.XPATH, ensure_visible=True).send_keys(nr_atendimento)
                bot.enter()
                consulta_realizada = True
            except:
                consulta_realizada = False

        # Se for a primeira pesquisa ou não for possível realizar a pesquisa pelo método anterior,
        # realizar o filtro a partir do botão com o símbolo da lupa.
        xpath = "//a[@class='btn inline-edit-link ng-scope']"
        if not bot.find_element(xpath, By.XPATH, waiting_time=0) or consulta_realizada is False:
            # Clicar no ícone de Pesquisar que fica no canto superior esquerdo
            xpath = "//div[div[@class='person-icon-finder']]"
            bot.find_element(xpath, By.XPATH).click()

            # Insere o número do atendimento no campo de pesquisa
            xpath = "//input[@name='NR_ATENDIMENTO']"
            bot.find_element(xpath, By.XPATH, ensure_clickable=True).clear()
            bot.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(nr_atendimento)

            # Clica no botão Filtrar
            bot.find_element("//button[contains(text(),'Filtrar')]", By.XPATH, ensure_clickable=True).click()

            # Duplo click na primeira linha da tabela de resultados
            if not browser.element_double_click(bot=bot, xpath=f"//div[div/div/span[text()='{nr_atendimento}']]"):
                raise Exception(["Excecao_Negocio", mensagem_erro + f"Atendimento ({nr_atendimento}) não localizado."])

        # Esperar a tela do PEPA carregar
        if not browser.element_wait_displayed(bot=bot, xpath="//span[text()='Agenda de consulta']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Tela do prontuário do paciente não localizada."])

        # Fechar qualquer popup de alerta que aparecer. Pode aparecer mais de 1
        for i in range(8):
            bot.key_esc(wait=1000)

        # Verifica se a tela do PEPA carregou
        if not bot.find_element("//div[text() = 'Paciente']", By.XPATH, ensure_visible=True, waiting_time=2000):
            raise Exception(["Excecao_Negocio", mensagem_erro + "Popup de erro localizado após pesquisa."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def acessar_consulta(bot: WebBot, dt_fim_consulta: str) -> None:
    """
    Função que seleciona a consulta baseado na data e hora do atendimento
    Args:
        bot: Objeto do navegador;
        dt_fim_consulta: data fim da consulta no formato DD/MM/YYYY HH:MI;
    """
    mensagem_erro = 'Falha ao acessar a consulta no PEPA. '
    try:
        # Clica na consulta desejada
        xpath = f"//span[contains(text(),'{dt_fim_consulta}')]"
        if not browser.element_click(bot=bot, xpath=xpath):
            raise Exception(['Excecao_Sistema', mensagem_erro + 'Consulta não localizada.'])

        # Valida se a consulta aparece na tabela central
        xpath = f"//div[div[div[span[contains(text(),'{dt_fim_consulta}')]]]]"
        if not bot.find_element(xpath, By.XPATH, ensure_visible=True):
            raise Exception(['Excecao_Sistema', 'Consulta não encontrada.'])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def gerar_relatorio_cate(bot: WebBot, dt_fim_consulta: str, cate: str) -> str:
    """
    Realiza o download de relatórios CATE de uma consulta específica.
    :param bot: Objeto do Tasy;
    :param dt_fim_consulta: Data fim da consulta;
    :param cate: Código do relatório CATE
    :return: Diretório completo do relatório CATE baixado.
    """
    mensagem_erro = f"Falha ao gerar relatório CATE-{cate}. "

    try:
        # Seleciona a consulta na tabela central de consultas
        xpath = f"//div[div[div[span[contains(text(),'{dt_fim_consulta}')]]]]"
        if not browser.element_click(bot=bot, xpath=xpath):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Consulta não localizada."])

        # Clica no menu "Relatórios -> Configurações"
        browser.element_click(bot=bot, xpath="//button[span[text()='Relatórios']]", delay=500)
        if not browser.element_click(bot=bot, xpath="//div[text()='Configurações']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Menu (Relatórios -> Configurações) não localizado."])

        # Preenche o campo 'Código'
        if not browser.element_set_text(bot=bot, xpath="//input[@name='CD_RELATORIO']", text=cate, delay=500):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Tela de pesquisa não localizada."])

        # Clica em 'Filtrar'
        if not browser.element_click(bot=bot, xpath="//button[contains(text(),'Filtrar')]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Filtrar) não localizado."])

        # Clica na linha referente ao CATE pesquisado
        if not browser.element_click(bot=bot, xpath=f"//div[div[div[span[text()='{cate}']]]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + f"CATE ({cate}) não localizado."])

        # Clica em 'Visualizar'
        if not browser.element_click(bot=bot, xpath="//button[span[text()='Visualizar']]", delay=500):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Visualizar) não localizado."])

        # Esperar o download ser concluído
        arquivo_baixado = esperar_conclusao_download(bot)

        # Clica em 'Cancelar'
        if not browser.element_click(bot=bot, xpath="//button[span[text()='Cancelar']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Cancelar) não localizado."])

        return arquivo_baixado

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)

