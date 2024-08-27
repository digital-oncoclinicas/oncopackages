# Bibliotecas Botcity
# ----------------------------------------------
from botcity.web.bot import WebBot, By

# ----------------------------------------------
# Bibliotecas Oncopackages
# ----------------------------------------------
from onco_packages.banco_dados.rpa import salvar_log_erro
from onco_packages.ferramentas.web_bot import element_get_text
from onco_packages.pastas_arquivos import pastas_arquivos

# ----------------------------------------------
# Bibliotecas locais
# ----------------------------------------------
import config
import sys


def login(bot: WebBot, codigo: str, usuario: str, senha: str):
    """
    Essa função faz login no site da Sul America
    :param bot: Objeto webBot
    :param codigo: Código do operador
    :param usuario: Usuário de acesso ao site da sulamerica
    :param senha: Senha de acesso ao site da sulamerica
    """

    # Declaração de Variáveis
    msg_erro_generica = 'Falha ao realizar login no site do convênio. '

    try:
        # Configurações iniciais do browser. Só é preciso informar na primeira execução
        if not bot.driver_path:

            # Define se o navegador vai ficar visível ou não
            bot.headless = config.HEADLESS

            # Define a pasta usada para salvar os downloads
            bot.download_folder_path = config.RPA_DIR_DOWNLOADS

            # Define o diretório do chromedriver.exe. Baixado do oncopachages.
            bot.driver_path = pastas_arquivos.chrome_driver_path()

        # Navegar em tela cheia
        bot.navigate_to('https://saude.sulamericaseguros.com.br/prestador/login')
        bot.maximize_window()

        # Verifica se está na tela de login
        if bot.find_element("user", By.ID, waiting_time=5000):
            # Informa o código
            bot.find_element("code", By.ID).send_keys(codigo)
            # Informa o usuário
            bot.find_element("user", By.ID).send_keys(usuario)
            # Informa o senha
            bot.find_element("senha", By.ID).send_keys(senha)
            # Clicar em Entrar
            bot.find_element('entrarLogin', By.ID).click()

            # Fechar mensagem
            if bot.find_element("//*[@id='sas-box-lgpd-info']//button", By.XPATH, ensure_clickable=True,
                                waiting_time=2000):
                bot.find_element("//*[@id='sas-box-lgpd-info']//button", By.XPATH).click()

            # Verificar se o login foi realizado com sucesso
            if element_get_text(bot, "//p[text()='Usuário ou Senha Inválidos!']", 5) != "":
                raise Exception(["Excecao_Negocio", "Usuário ou Senha Inválidos."])
            elif bot.find_element("//*[@title='Voltar a Home']", By.XPATH, waiting_time=20000):
                return
            else:
                raise Exception(["Excecao_Sistema", msg_erro_generica])

    except Exception:
        error_message = salvar_log_erro(sys, msg_erro_generica, bot)
        raise ValueError(error_message)

