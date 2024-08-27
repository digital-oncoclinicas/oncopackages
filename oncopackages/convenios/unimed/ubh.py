from onco_packages.banco_dados.rpa import salvar_log_erro
from onco_packages.pastas_arquivos import pastas_arquivos
from botcity.web import WebBot, By
import config
import sys
import re


def login(bot: WebBot, usuario: str, senha: str) -> None:
    """
    Realiza login no site do convênio Unimed BH.
    :param bot: Objeto do navegador.
    :param usuario: Usuário;
    :param senha: Senha.
    """
    mensagem_erro = "Falha ao realizar login no site da Unimed BH. "
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
        bot.navigate_to("https://www12.unimedbh.com.br/unioffice/home.do")

        # Navegador em tela cheia
        bot.maximize_window()

        # Informa o usuário
        bot.find_element("username", By.ID, waiting_time=30000, ensure_clickable=True).send_keys(usuario)

        # Informa o senha
        bot.find_element("password", By.ID).send_keys(senha)

        # Entrar
        bot.enter()

        # Verificar se o login foi realizado com sucesso.
        if bot.find_element("//td[text()='Página Inicial']", By.XPATH, ensure_visible=True):
            return

        # Verificar se a senha está inválida
        if bot.find_element("//div[contains(text(),'Credenciais inválidas!')]", By.XPATH, 1000):
            raise Exception(["Excecao_Negocio", mensagem_erro + "Credenciais inválidas!"])

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def consultar_cobertura_beneficiario(bot: WebBot, carteirinha: str) -> dict:
    """
    Consulta a situação e cobertura da elegibilidade de beneficiários Unimed BH.
    :param bot: Objeto do navegador.
    :param carteirinha: Carteirinha do paciente.
    :return dicionário com as chaves Produto, Situação, Rede e Tipo de acomodação.
    """
    mensagem_erro = "Falha ao consultar a cobertura do beneficiário. "
    try:

        # Acessar a tela de pesquisa
        bot.navigate_to("https://www12.unimedbh.com.br/unioffice/conteudoConsultasSituacaoCobertura.do")

        # Remove qualquer caractere não numérico
        carteirinha = re.sub(r'[^0-9]', '', carteirinha)

        # Preencha com zeros à esquerda até completar 17 caracteres
        carteirinha = carteirinha.zfill(17)

        # Preenche o campo Código do beneficiário
        bot.find_element("codigo_cliente", By.NAME).send_keys(carteirinha)
        bot.enter()

        # Deixa a carteirinha com a formatação do site "0.006.0502.982.284.00-0"
        cart_formatada = re.sub(r'(\d)(\d{3})(\d{4})(\d{3})(\d{3})(\d{2})(\d)$', r'\1.\2.\3.\4.\5.\6-\7', carteirinha)

        # Verificar se o site localizou o beneficiário
        if not bot.find_element(f"//td[contains(text(),'{cart_formatada}')]", By.XPATH):
            raise Exception(["Excecao_Negocio", mensagem_erro + f"Beneficiário ({carteirinha}) não localizado."])

        produto = bot.find_element("//tr[td[contains(text(),'Produto')]]/td[2]", By.XPATH).text
        situacao = bot.find_element("//tr[td[contains(text(),'Situação')]]/td[2]", By.XPATH).text
        rede = bot.find_element("//tr[td[contains(text(),'Rede')]]/td[2]", By.XPATH).text
        tipo_acomodacao = ""
        xpath = "//tr[td[*[contains(text(),'Tipo de Acomodação')]]]/td[2]"
        if bot.find_element(xpath, By.XPATH, waiting_time=100):
            tipo_acomodacao = bot.find_element(xpath, By.XPATH).text

        return {"Produto": produto,
                "Situação": situacao,
                "Rede": rede,
                "Tipo de acomodação": tipo_acomodacao}

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)

