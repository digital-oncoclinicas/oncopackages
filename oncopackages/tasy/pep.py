from onco_packages.banco_dados.rpa import salvar_log_erro
from botcity.web.bot import ActionChains
from botcity.web import By
import sys


def pesquisar_prontuario(bot, nr_prontuario: str, acessar_prontuario: bool = False):
    try:
        # Espera a tela carregar
        xpath = "//div[div[@class='person-icon-finder']]"
        if not bot.find_element(xpath, By.XPATH, waiting_time=15000, ensure_clickable=True):
            raise Exception(["Excecao_Sistema", "Botão Ações de pesquisa não localizado na função PEP."])
        bot.wait(1000)

        # Clicar no ícone de Pesquisar que fica no canto superior esquerdo
        xpath = "//div[div[@class='person-icon-finder']]"
        bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).click()

        # Clicar no ícone de Filtro que fica no canto superior esquerdo
        xpath = "//div[@tab-tooltip='Pessoa']"
        bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).click()

        # Insere o numero do prontuario no campo de '
        xpath = "//input[@name='CD_PESSOA_FISICA_WJTF']"
        bot.find_element(xpath, By.XPATH, ensure_clickable=True).clear()
        bot.find_element(xpath, By.XPATH, ensure_clickable=True).send_keys(nr_prontuario)

        # Clica no botão Filtrar
        bot.find_element("//button[contains(text(), 'Filtrar')]", By.XPATH).click()

        # Duplo click na primeira linha da tabela de autorizações
        if acessar_prontuario:
            action = ActionChains(bot.driver)
            elemento = bot.find_element('(//div[@data-row-idx="0"])[3]', By.XPATH, ensure_clickable=True)
            action.double_click(elemento).perform()

            if not bot.find_element("//div[span='Dados do paciente/médico']", By.XPATH):
                raise Exception(["Excecao_Sistema", "Tela de prontuario do paciente não localizada."])

    except Exception:
        error_message = salvar_log_erro(sys, "Falha ao pesquisar pelo prontuario no PEP. ", bot)
        raise ValueError(error_message)
