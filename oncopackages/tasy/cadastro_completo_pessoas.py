from onco_packages.banco_dados.rpa import salvar_log_erro
from botcity.web.bot import ActionChains, WebBot, By, Keys
import datetime
import sys


def pesquisar_prontuario(bot: WebBot, prontuario: str):
    """
    Pesquisar pelo prontuário do paciente na função 'Cadastro Complementar de Pessoas' do Tasy.
    :param bot: Objeto da BotCity;
    :param prontuario: Prontuário do paciente.
    """

    mensagem_erro = "Falha ao pesquisar pelo prontuário na função Cadastro Completo de Pessoas. "

    try:
        # Espera a tela carregar
        xpath = "//div[div[contains(@ng-if, 'locator')]]"
        if not bot.find_element(xpath, By.XPATH, waiting_time=30000, ensure_clickable=True):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão Pesquisar não localizado."])

        # Se não for a primeira pesquisa, realizar o filtro a partir do campo 'Código' da barra superior.
        consulta_realizada = False
        xpath = "//a[@class='btn inline-edit-link ng-scope']"
        if bot.find_element(xpath, By.XPATH, waiting_time=2000):
            # Clica no desenho do lapis para editar o campo 'Código'
            action = ActionChains(bot.driver)
            elemento = bot.find_element(xpath, By.XPATH)
            action.click(elemento).perform()

            # Insere o prontuário e tecla 'Enter' para pesquisar
            xpath = "//div[span[text()='Código']]/div/span/input"
            if bot.find_element(xpath, By.XPATH, waiting_time=2000, ensure_visible=True):
                bot.find_element(xpath, By.XPATH, ensure_visible=True).send_keys(prontuario)
                bot.enter()
                consulta_realizada = True

        # Se for a primeira pesquisa ou não for possível realizar a pesquisa pelo método anterior,
        # realizar o filtro a partir do botão com o símbolo da lupa.
        if not consulta_realizada:
            # Clicar no ícone de Pesquisar que fica no canto superior esquerdo
            xpath = "//div[div[@class='person-icon-finder']]"
            bot.find_element(xpath, By.XPATH).click()

            # Insere o número do prontuário no campo de pesquisa
            xpath = "//input[contains(@name, 'CD_PESSOA_FISICA_')]"
            bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).clear()
            bot.wait(1000)
            bot.find_element(xpath, By.XPATH).send_keys(prontuario)

            # Clica no botão Filtrar
            bot.find_element("//button[contains(text(),'Filtrar')]", By.XPATH, ensure_clickable=True).click()

            # Espera o prontuário aparecer na tabela de resultados
            xpath = f"//div[div/div/span[text()='{prontuario}']]"
            if not bot.find_element(xpath, By.XPATH):
                raise Exception(["Excecao_Negocio", mensagem_erro + "Prontuario não localizado."])

            # Clica no botão 'Ok'
            xpath = "//button[span[text() = 'Ok']]"
            bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

        # Esperar a tela de resultado carregar
        if not bot.find_element("//span[text() = 'Nacionalidade']", By.XPATH):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Tela de cadastro do paciente não localizada."])

        # Fechar qualquer popup de alerta que aparecer.
        # Pode aparecer mais de 1
        for i in range(6):
            bot.key_esc(wait=1000)

        # Verifica se ainda há algum popup na tela
        if not bot.find_element("//span[text() = 'Nacionalidade']", By.XPATH, 2000, True):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Popup de alerta localizado."])
        
    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def acessar_aba_classificacao_paciente(bot: WebBot):
    """
    Acessa a aba 'Classificação do paciente'.
    :param bot: Objeto do navegador Tasy.
    """

    mensagem_erro = "Falha ao acessar a aba Classificação do Paciente. "

    try:
        # Se a opção 'Informação adicional' já estiver selecionada, nada precisa ser feito.
        xpath = "//div[a[ng-include[span[text() = 'Informação adicional']]]]"
        if bot.find_element(xpath, By.XPATH, waiting_time=3000, ensure_clickable=True):
            # Já se encontra com a opção correta selecionada
            bot.wait(3000)  # Espera necessária para a página carregar completamente
            return

        # Clica no botão 'Complemento' para abrir a lista suspensa.
        # Botão localizado no canto superior esquerdo da segunda tela, acima do label 'Todos complementos'
        xpath = "//div[a[ng-include[span[text() = 'Complemento']]]]"
        bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

        # Seleciona a opção 'Informação adicional'
        xpath = "//a[span[text() = 'Informação adicional']]"
        bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

        # Clica na aba 'Classificações do paciente'
        xpath = "//div[span[contains(text(), 'Classificaçõe')]]"
        if bot.find_element(xpath, By.XPATH, waiting_time=3000, ensure_clickable=True):
            bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
        # Se a aba 'Classificações do paciente' não estiver visível
        else:
            # Clicar nos (...) que fica no canto superior direito da segunda tela
            bot.find_element('elipsisButton', By.ID, ensure_clickable=True).click()

            # Clica na aba 'Classificações do paciente'
            xpath = "//div[contains(text(), 'Classificaçõe')]"
            bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

            # Clicar nos (...) novamente para ocultar a lista suspensa
            bot.find_element('elipsisButton', By.ID, ensure_clickable=True).click()

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def atualizar_fim_vigencia(bot: WebBot, observacao: str):
    """
    Atualizar a data fim de vigência de todas as classificações.
    :param bot: Objeto do navegador Tasy.
    :param observacao: Texto que será adicionado ao campo observação da classificação.
    """

    mensagem_erro = "Falha ao atualizar a data fim de vigência. "
    data_atual = datetime.date.today()

    try:
        # Contar a quantidade de linhas que tem na tabela de classificações
        xpath = "//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div"
        qt_classif = len(bot.find_elements(xpath, By.XPATH))
        for n in range(0, qt_classif):

            # pega a data fim de vigência
            xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]/div[3]"
            data_fim_vigencia = browser.element_get_text(bot=bot, xpath=xpath)
            data_fim_vigencia = data_fim_vigencia.replace('\u202a', '').replace('\u202c', '')
            if data_fim_vigencia != '':
                data_fim_vigencia = datetime.datetime.strptime(data_fim_vigencia, '%d/%m/%Y %H:%M:%S').date()

            if data_fim_vigencia == '' or data_fim_vigencia > data_atual:
                # Clica na linha da tabela
                xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]"
                browser.element_click(bot=bot, xpath=xpath, delay=500)

                # Clica em 'Ver'
                if not browser.element_click(bot=bot, xpath="//button[span[text() = 'Ver']]", delay=1000):
                    raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Ver) não localizado."])

                # Preencher campo 'Fim vigência' com o primeiro dia do mês seguinte ao atual
                data_fim_vigencia = primeiro_dia_mes_seguinte()
                xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
                if not browser.element_set_text(bot=bot, xpath=xpath, text=data_fim_vigencia, delay=1000):
                    raise Exception(["Excecao_Sistema", mensagem_erro + "Campo (Data final de vigência) não localizado."])

                # Preencher campo 'Observação'
                xpath = "//div[div[div[div[contains(text(),'Classificações do paciente')]]]]" \
                        "//textarea[@name='DS_OBSERVACAO']"
                bot.find_element(xpath, By.XPATH).clear()
                bot.find_element(xpath, By.XPATH).send_keys(observacao)

                # Clica no botão 'Salvar'
                xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
                bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

                # Verifica se salvou com sucesso
                xpath = f"//div[div[div[div[div[span[text() = 'Classificações']]]]]]/div[4]/div[3]/div/div[{n + 1}]"
                if not bot.find_element(xpath, By.XPATH, ensure_visible=True):
                    raise Exception(["Excecao_Sistema", mensagem_erro + "Não foi possível confirmar a atualização."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def adicionar_classificacao_paciente(bot: WebBot, classificacao: str, data_fim_vigencia: str = '',
                                     data_inicio_vigencia: str = ''):
    """
    Informa a Classificação, a data fim de vigência, o campo observação e salva.
    :param bot: Objeto do navegador Tasy.
    :param classificacao: Classificação do paciente;
    :param data_inicio_vigencia: Data de início da vigência da classificação
    :param data_fim_vigencia: Data fim de vigência.
    """

    mensagem_erro = "Falha ao adicionar classificação do paciente. "

    try:
        # Clica no botão 'Adicionar'
        xpath = "//div[div[div[div[contains(text(), 'Classificações do paciente')]]]]" \
                "//*[contains(text(), 'Adicionar')]"
        if not browser.element_click(bot=bot, xpath=xpath):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Adicionar) não localizado."])

        # Informa a classificação
        xpath = "//div[div[span[text() = 'Classificação']]]/div[2]/tasy-listbox/div"
        browser.element_click(bot=bot, xpath=xpath, delay=500)
        if not browser.element_click(bot=bot, xpath=f"//a[span[text() = '{classificacao}']]", delay=500):
            raise Exception(["Excecao_Negocio", mensagem_erro + f"Classificação ({classificacao}) não localizada."])

        # Preencher campo 'Início vigência'
        if data_inicio_vigencia != '':
            xpath = "//*[@name= 'DT_INICIO_VIGENCIA']"
            if not browser.element_wait_displayed(bot=bot, xpath=xpath):
                raise Exception(["Excecao_Sistema", mensagem_erro + "Campo (Início da vigência) não localizado."])
            bot.find_element(selector=xpath, by=By.XPATH).click()
            bot.type_keys(keys=[Keys.CONTROL, "a"])
            bot.kb_type(data_inicio_vigencia)

        # Preencher campo 'Fim vigência'
        if data_fim_vigencia != '':
            xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
            if not browser.element_set_text(bot=bot, xpath=xpath, text=data_fim_vigencia, delay=1000):
                raise Exception(["Excecao_Sistema", mensagem_erro + "Campo (Final vigência) não localizado."])

        # Clica no botão 'Salvar'
        xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
        bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()

        # Verifica se salvou com sucesso
        xpath = f"(//div[contains(@data-row-idx, '0')])[2]"
        if bot.find_element(xpath, By.XPATH, ensure_visible=True):
            return

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def atualizar_fim_vigencia_classificacao_anterior(bot: WebBot, classif_anterior: str):
    """
    Atualizar a data fim de vigência da classificação anterior.
    :param bot: Objeto do navegador Tasy.
    :param classif_anterior: Classificação cuja data fim de vigência deve ser atualizada.
    """

    mensagem_erro = "Falha ao atualizar a data fim de vigência da classificação anterior. "

    try:
        # Verifica se existe a classificação anterior
        xpath = f"//div[div[div[span[contains(text(),'{classif_anterior}')]]]]"
        if not bot.find_element(xpath, By.XPATH):
            raise Exception(["Excecao_Negocio", mensagem_erro + f"Classificação ({classif_anterior}) não localizada."])

        # Clica na linha da tabela
        bot.find_element(xpath, By.XPATH, waiting_time=15000).click()

        # Clica em 'Ver'
        if not browser.element_click(bot=bot, xpath="//button[span[text() = 'Ver']]", delay=1000):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Ver) não localizado."])

        # Preencher campo 'Fim vigência' com a data de hoje
        data_atual = datetime.datetime.now()
        data_fim_vigencia = data_atual.strftime("%d%m%Y%H%M%S")
        xpath = "//*[@name= 'DT_FINAL_VIGENCIA']"
        if not browser.element_set_text(bot=bot, xpath=xpath, text=data_fim_vigencia, delay=1000):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Campo (Data final de vigência) não localizado."])
        data_fim_vigencia = data_atual.strftime("%d/%m/%Y %H:%M:%S")

        # Clica no botão 'Salvar'
        xpath = "//div[div[div[span[contains(text(), 'Salvar')]]] and contains(@class, 'enable')]"
        if bot.find_element(xpath, By.XPATH, ensure_clickable=True):
            bot.find_element(xpath, By.XPATH, ensure_clickable=True).click()
        else:  # Se o botão 'Salvar' não estiver ativo, clicar em 'Fechar'
            if not browser.element_click(bot, "//button[span[contains(text(), 'Fechar')]]"):
                raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Fechar) não localizado."])

        # Verifica se salvou com sucesso
        xpath = f"//div[div[div[span[contains(text(),'{data_fim_vigencia}')]]]]"
        if bot.find_element(xpath, By.XPATH, ensure_visible=True):
            return

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def primeiro_dia_mes_seguinte() -> str:
    """
    Calcula a data do primeiro dia do mês seguinte ao atual.
    :return: Data do primeiro dia do mês seguinte.
    """
    mensagem_erro = "Falha ao calcular o primeiro dia do mês seguinte."

    try:
        # Obtém a data atual
        data_atual = datetime.date.today()
        # Obtém o primeiro dia do mês seguinte
        nova_data = data_atual.replace(day=1) + datetime.timedelta(days=32)
        nova_data = nova_data.replace(day=1)
        # Formata a nova data
        nova_data = nova_data.strftime("%d%m%Y") + '235959'

        return nova_data

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro)
        raise ValueError(error_message)

