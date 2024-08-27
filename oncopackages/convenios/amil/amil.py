from onco_packages.banco_dados.rpa import salvar_log_erro
from onco_packages.pastas_arquivos import pastas_arquivos
from botcity.web import WebBot, By
import config
import sys


def login(bot: WebBot, usuario: str, senha: str):
    """
    Realiza o login no site do convênio Amil.
    :param bot: Objeto da BotCity;
    :param usuario: Usuário;
    :param senha: Senha.
    """
    mensagem_erro = "Falha ao realizar login no site da Amil. "

    try:
        # Define se o navegador vai ficar visível ou não
        bot.headless = config.HEADLESS

        # Define a pasta usada para salvar os downloads
        bot.download_folder_path = config.RPA_DIR_DOWNLOADS

        # Baixa o WebDriver compatível com a versão do navegador, caso necessário
        if not bot.driver_path:
            bot.driver_path = pastas_arquivos.chrome_driver_path()

        # Abre o navegador e acessa o site do convênio
        bot.navigate_to("https://credenciado.amil.com.br/login")

        # Navegador em tela cheia
        bot.maximize_window()

        # Espera a tela carregar
        if not bot.find_element("login-usuario", By.ID, waiting_time=30000, ensure_visible=True):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Site indisponível."])

        # Verificar se o popup com orientações do login está ativo
        if bot.find_element("finalizar-walktour", By.ID, waiting_time=1000):
            bot.find_element("finalizar-walktour", By.ID).click()

        # Informa o usuário
        bot.find_element("login-usuario", By.ID, ensure_clickable=True).send_keys(usuario)

        # Informa o senha
        bot.find_element("login-senha", By.ID).send_keys(senha)

        # Entrar
        bot.find_element("//button[text()='Entrar']", By.XPATH).click()

        # Verificar se o login foi realizado com sucesso
        if bot.find_element("//span[contains(text(),'Nome')]", By.XPATH, waiting_time=30000):
            return

        # Verificar se a senha está errada
        if bot.find_element("//p[text()='Usuário ou senha inválido.']", By.XPATH, waiting_time=0):
            raise Exception(["Excecao_Negocio", mensagem_erro + "Usuário ou senha inválido."])

        # Verificar se o Serviço está indisponível no momento.
        if bot.find_element("//p[text()='Serviço indisponível no momento.']", By.XPATH, waiting_time=0):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Serviço indisponível no momento."])

        # Reportar falha genérica
        raise Exception(["Excecao_Sistema", mensagem_erro])

    except:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)

