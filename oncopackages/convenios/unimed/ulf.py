from onco_packages.banco_dados.rpa import salvar_log_erro
from onco_packages.pastas_arquivos import pastas_arquivos
from botcity.web import WebBot, By
import config
import sys


def login(bot: WebBot, usuario: str, senha: str):
    """
    Essa função faz login no site da ULF
    :param bot: Objeto webBot
    :param usuario: usuário para login no site da ULF
    :param senha: senha para login no site da ULF
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

            # Define o diretório do chromedriver.exe. Baixa da rede caso necessário.
            bot.driver_path = pastas_arquivos.chrome_driver_path()

        # Navegar até a tela de login
        bot.navigate_to('https://remote.unimedlestefluminense.coop.br/connecta')

        # Tela cheia
        bot.maximize_window()

        # Verifica se está na tela de login
        if bot.find_element("txbUsuario", By.ID, waiting_time=5000):
            # Informa o usuário
            bot.find_element("txbUsuario", By.ID).send_keys(usuario)
            # Informa o senha
            bot.find_element("txbSenha", By.ID).send_keys(senha)
            # Clicar em Entrar
            bot.find_element('btnEntrar', By.ID).click()

            # Verificar se o login foi realizado com sucesso
            if bot.find_element("cphConteudo_ltvAtalhos_hplAtalho_0", By.ID, waiting_time=20000):
                return

            # Checar mensagem erro
            if bot.find_element("modalContentAlert", By.ID, waiting_time=1000):
                erro = bot.find_element("modalContentAlert", By.ID).get_attribute('innerText')
                if 'usuário e/ou senha estão corretos' in erro:
                    raise Exception(["Excecao_Negocio", 'Usuário e/ou senha estão incorretos.'])
                else:
                    raise Exception(["Excecao_Negocio", f'{mensagem_erro}{erro}'])

            raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)

