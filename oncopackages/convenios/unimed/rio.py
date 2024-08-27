from onco_packages.banco_dados.rpa import salvar_log_erro
from onco_packages.pastas_arquivos import pastas_arquivos
from onco_packages.ferramentas.web_bot import element_click
from botcity.web import WebBot, By
import config
import sys


def login(bot: WebBot, usuario: str, senha: str) -> None:
    """
    Essa função faz login no site da Unimed Rio.
    :param bot: Objeto webBot;
    :param usuario: Usuário;
    :param senha: Senha.
    """

    # Declaração de Variáveis
    mensagem_erro = 'Falha ao realizar login no site do convênio. '

    try:

        # Configurações iniciais do browser. Só é preciso informar na primeira execução
        if not bot.driver_path:

            # Define se o navegador vai ficar visível ou não
            bot.headless = config.HEADLESS

            # Define a pasta usada para salvar os downloads
            bot.download_folder_path = config.RPA_DIR_DOWNLOADS

            # Define o diretório do chromedriver.exe. Baixado do oncopachages.
            bot.driver_path = pastas_arquivos.chrome_driver_path()

        # Abre o navegador e acessa o site do convênio
        bot.navigate_to("https://producaoonline.unimedrio.com.br/prestador/Home/Index")

        # Navegador em tela cheia
        bot.maximize_window()

        # Fechar pop-ups
        xpath = "//button[text()='Ok']"
        element_click(bot, xpath=xpath, tentativas=5)

        # Informa o usuário
        bot.find_element("login", By.ID, waiting_time=20000, ensure_clickable=True).send_keys(usuario)

        # Informa o senha
        bot.find_element("pass", By.ID).send_keys(senha)

        # Entrar
        bot.enter()

        # Verificar se a senha está incorreta
        if bot.find_element("//*[contains(text(), 'A senha informada está incorreta.')]", By.XPATH, waiting_time=1000):
            raise Exception(["Excecao_Negocio", mensagem_erro + "Usuário ou senha inválidos."])

        # Verificar se o login foi realizado com sucesso
        if bot.find_element("//a[contains(text(), 'Home')]", By.XPATH, waiting_time=20000):
            return

        # Reportar falha genérica
        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)

