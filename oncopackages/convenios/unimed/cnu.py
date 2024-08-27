from onco_packages.ferramentas.web_bot import (element_wait_displayed, element_left_click, element_set_text,
                                               element_get_text, element_get_value)
from onco_packages.banco_dados.rpa import salvar_log_erro
from onco_packages.pastas_arquivos import pastas_arquivos
from selenium.webdriver.support.select import Select
from botcity.web import WebBot, By
import config
import sys


def login_saw(bot: WebBot, usuario: str, senha: str) -> None:
    """
    Realiza login no site do convênio Central Nacional Unimed
    :param bot: Objeto do navegador.
    :param usuario: Usuário;
    :param senha: Senha.
    """
    mensagem_erro = "Falha ao realizar login no site da CNU-SAW. "
    try:

        # Configurações iniciais do browser. Só é preciso informar na primeira execução
        if not bot.driver_path:

            # Define se o navegador vai ficar visível ou não
            bot.headless = config.HEADLESS

            # Define a pasta usada para salvar os downloads
            bot.download_folder_path = config.RPA_DIR_DOWNLOADS

            # Define o diretório do chromedriver.exe. Baixa da rede caso necessário.
            bot.driver_path = pastas_arquivos.chrome_driver_path()

        # Abre o navegador e acessa o site do convênio
        bot.navigate_to("https://saw.trixti.com.br/saw")

        # Navegador em tela cheia
        bot.maximize_window()

        # Informa o usuário
        bot.find_element("login", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(usuario)

        # Informa o senha
        bot.find_element("password", By.ID).send_keys(senha)

        # Entrar
        bot.enter()

        # Verificar se o login foi realizado com sucesso.
        if bot.find_element("//label[text()='Principal']", By.XPATH, ensure_visible=True):
            return
        else:  # Às vezes a página cai ao realizar login pela segunda vez. Solução de contorno
            bot.navigate_to("https://saw.trixti.com.br/saw")
            if bot.find_element("//label[text()='Principal']", By.XPATH, ensure_visible=True):
                return

        # Verificar se a senha está errada
        if (bot.find_element("//div[contains(*, 'senha inválida')]", By.XPATH, 0, True)
                or bot.find_element("//div[contains(*, 'Senha incorreta')]", By.XPATH, 0, True)):
            raise Exception(["Excecao_Negocio", mensagem_erro + "Senha/Login Incorreto."])

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def login_portal(bot: WebBot, usuario: str, senha: str) -> None:
    """
    Realiza login no portal de serviços On-Line do prestador do convênio Central Nacional Unimed
    :param bot: Objeto do navegador.
    :param usuario: Usuário;
    :param senha: Senha.
    """
    mensagem_erro = "Falha ao realizar login no site da CNU-Portal. "
    try:

        # Configurações iniciais do browser. Só é preciso informar na primeira execução
        if not bot.driver_path:

            # Define se o navegador vai ficar visível ou não
            bot.headless = config.HEADLESS

            # Define a pasta usada para salvar os downloads
            bot.download_folder_path = config.RPA_DIR_DOWNLOADS

            # Define o diretório do chromedriver.exe. Baixa da rede caso necessário.
            bot.driver_path = pastas_arquivos.chrome_driver_path()

        # Abre o navegador e acessa o site do convênio
        bot.navigate_to("https://www1.centralnacionalunimed.com.br/psp/menu.jsf")

        # Navegador em tela cheia
        bot.maximize_window()

        # Informa o usuário
        bot.find_element("j_username", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(usuario)

        # Informa o senha
        bot.find_element("j_password", By.ID).send_keys(senha)

        # Entrar
        bot.enter()

        # Verificar se o login foi realizado com sucesso.
        if bot.find_element("//a[text()='Sair']", By.XPATH, ensure_visible=True):
            # # Após confirmação do login, o site exibe 4 popups que possuem o mesmo xpath e estão todos visíveis.
            # # Por isso foi necessário especificar o popup pelo ID.
            # # A ordem dos popups muda. Por isso tentamos clicar em todos 3 vezes
            # for n in range(3):
            #     # Popup de alerta 1
            #     element_left_click(bot=bot, xpath="//input[@value='Fechar']", tentativas=1, delay=250)
            #     # Popup de alerta 2
            #     element_left_click(bot=bot, xpath="//*[@id='frm:btnErrorClose2']", tentativas=1, delay=250)
            #     # Popup de alerta 3
            #     element_left_click(bot=bot, xpath="//*[@id='frm:btnMpMsg2']", tentativas=1, delay=250)
            #     # Popup de alerta 4
            #     element_left_click(bot=bot, xpath="//*[@id='frm:btnMpMsgERecGlosa']", tentativas=1, delay=250)

            return

        # Verificar se a senha está errada
        if element_wait_displayed(bot=bot, xpath="//span[contains(text(),'Tente novamente')]", tentativas=1):
            raise Exception(["Excecao_Negocio", mensagem_erro + "Senha/Login Incorreto."])

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def consultar_elegibilidade_carteirinha(bot: WebBot,
                                        codigo_prestador: str,
                                        carteirinha: str,
                                        cnu_user: str,
                                        cnu_pwd: str) -> dict:
    """
    Consulta a elegibilidade da carteirinha no site do convênio Central Nacional Unimed.
    :param bot: Objeto do navegador;
    :param carteirinha: Carteirinha no paciente;
    :param codigo_prestador: Código do Oncoclínicas no portal;
    :param cnu_user: Usuário do portal da CNU;
    :param cnu_pwd: Senha do portal da CNU.
    :return: Dicionário com a validade da carteirinha e a elegibilidade.
    """
    mensagem_erro = "Falha ao consultar a elegibilidade da carteirinha no portal da CNU. "
    try:
        # O portal da CNU, aleatóriamente realiza o sign out e é necessário realizar sing in novamente.
        for n in range(5):
            # Realiza o login caso necessário
            if not bot.capabilities or bot.find_element("j_username", By.ID, waiting_time=0):
                login_portal(bot=bot, usuario=cnu_user, senha=cnu_pwd)

            # Acessando o menu 'Autorização'
            if not element_wait_displayed(bot=bot, xpath="//*[text()='Elegibilidade']", tentativas=4):
                bot.navigate_to("https://www1.centralnacionalunimed.com.br/auto/blank.jsf")

            # Clica no menu 'Elegibilidade'
            if element_left_click(bot=bot, xpath="//*[@id='frmMenuElegibilidade']", delay=500):
                break

        if not element_wait_displayed(bot=bot, xpath="//span[text()='Elegibilidade']", tentativas=4):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Tela de pesquisa não localizada."])

        # Preencher o campo 'Código Prestador:'
        select = Select(bot.find_element("frm:selectCodigoPrestador", By.ID))
        select.select_by_visible_text(codigo_prestador)

        # No campo 'Código do Cartão:', preencher com a carteirinha e teclar TAB
        element_set_text(bot=bot, xpath="//input[@id='frm:cartao']", text=carteirinha)
        bot.tab()

        # Espera retorno do site
        if not element_wait_displayed(bot=bot, xpath="//input[@value='Imagem da Carteirinha']", tentativas=60):
            raise Exception(["Excecao_Sistema", mensagem_erro + "O portal não retornou um resultado."])

        # Pega validade da carteirinha
        validade = element_get_value(bot=bot, xpath="//td[span[text()='Validade do Cartão:']]/input", delay=1000)

        # Elegibilidade da carteirinha
        elegibilidade = element_get_text(bot=bot, xpath="//tr[11]/td/span", delay=1000)
        if not elegibilidade:
            raise Exception(["Excecao_Sistema", mensagem_erro + "Resposta do portal não localizada."])

        # Pega o retorno do site
        return {'data_validade': validade, 'elegibilidade': elegibilidade}

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)

