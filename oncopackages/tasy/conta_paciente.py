from onco_packages.ferramentas.web_bot import (element_click, element_get_text, element_wait_displayed,
                                               element_set_text, element_right_click, element_double_click,
                                               element_left_click, element_get_value)
from onco_packages.banco_dados.tasy.conta_paciente import confirmar_taxa_adicionada
from onco_packages.banco_dados.rpa import salvar_log_erro
from botcity.web.bot import ActionChains
from botcity.web import By, WebBot
import sys
import re


def pesquisar_conta(bot: WebBot, nr_conta: str) -> None:
    """
    Função que realiza a pesquisa pelo número conta na função 'Conta Paciente' do Tasy.
    Args:
        bot: Objeto do Navegador.
        nr_conta: Número da conta paciente a ser pesquisada.
    """
    mensagem_erro = "Falha ao pesquisar pela conta na função 'Conta Paciente'. "
    try:
        # Valida se a tela de filtro de pesquisa pela conta carregou corretamente
        xpath = f"//button[contains(text(),'Filtrar')]"
        if not bot.find_element(xpath, By.XPATH, ensure_visible=True, ensure_clickable=True):
            try:
                # Clicar no ícone de Filtro que fica no canto superior esquerdo
                xpath = f"//tasy-wlabel[@uib-tooltip='Filtros em uso (Ctrl + Alt + F)'][@tooltip-append-to-body='true']"
                bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True).click()
            except:
                raise Exception(["Excecao_sistema", mensagem_erro + "Filtro pesquisar conta não localizado."])

        # Verifica se o campo de pesquisa da conta paciente está disponível na tela
        if not bot.find_element(xpath, By.XPATH, ensure_clickable=True, ensure_visible=True):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Campo inserir o número da conta não localizado."])

        # Insere o Número da conta no campo de pesquisa
        xpath = "//input[@name='NR_INTERNO_CONTA']"
        if not element_set_text(bot=bot, xpath=xpath, text=nr_conta, delay=1000):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Campo (Número da conta) não localizado."])

        # Clica no botão de 'filtro'
        xpath = f"//button[contains(text(),'Filtrar')]"
        bot.find_element(xpath, By.XPATH, ensure_visible=True, ensure_clickable=True).click()

        # Valida se a pesquisa retornou a conta
        xpath = f"//div[span[text()='{nr_conta}']]"
        if not bot.find_element(xpath, By.XPATH, ensure_visible=True):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Conta não foi localizada."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def pesquisar_atendimento(bot: WebBot, atendimento: str) -> None:
    """
    Função que realiza a pesquisa pelo número do atendimento na função 'Conta Paciente' do Tasy.
    Args:
        bot: Objeto do Navegador.
        atendimento: Número do atendimento do paciente a ser pesquisado.
    """
    mensagem_erro = "Falha ao pesquisar pelo atendimento na função 'Conta Paciente'. "
    consulta_realizada = False

    try:
        # Verifica se é possível pesquisar a partir da barra superior. Isso só é possível a partir da segunda pesquisa.
        xpath = "//a[@class='btn inline-edit-link ng-scope']"
        if bot.find_element(xpath, By.XPATH, waiting_time=0):
            # Clica no desenho de um lapis no campo 'Atendimento'
            element = bot.find_element(xpath, By.XPATH, waiting_time=0)
            action = ActionChains(bot.driver)
            action.click(element).perform()

            # Preenche o campo 'Atendimento'
            xpath = "//input[@ng-if='inlineEditActive']"
            if bot.find_element(xpath, By.XPATH, waiting_time=2000):
                bot.find_element(xpath, By.XPATH).send_keys(atendimento)
                bot.enter()
                consulta_realizada = True

        # Caso seja a primeira consulta ou não foi possível realizar a pesquisa pelo método anterior:
        if not consulta_realizada:
            # Preenche o campo 'Atendimento'
            element_set_text(bot=bot, xpath="//input[contains(@name,'NR_ATENDIMENTO')]", text=atendimento, delay=1000)

            # Clica no botão 'Filtrar'
            element_click(bot=bot, xpath="//button[contains(text(),'Filtrar')]")

        # Espera o campo 'Atendimento' ser atualizado para o atendimento pesquisado
        if element_wait_displayed(bot=bot, xpath=f"//span[@id='NR_ATENDIMENTO']/span[text()='{atendimento}']"):
            return

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def acessar_conta(bot: WebBot, conta: str) -> None:
    """
    Duplo click na linha referente a conta da função 'Conta Paciente' do Tasy.
    :param: bot: Objeto do Navegador.
    :param: conta: Conta que será acessada.
    """
    mensagem_erro = "Falha ao acessar a conta na função 'Conta Paciente'. "

    try:
        # Clica para ativar a linha da canta na tabela.
        xpath = f"//div[span[text()='{conta}']]"
        if not element_click(bot=bot, xpath=xpath, delay=1000):
            raise Exception(["Excecao_Negocio", mensagem_erro + f"Conta ({conta}) não localizada."])

        # Duplo click para acessar a conta
        element_double_click(bot=bot, xpath=xpath, delay=1000)

        # Valido carregamento da tela de detalhes da conta
        if not element_wait_displayed(bot=bot, xpath="//span[contains(text(), 'Procedimentos')]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Tela de detalhes da conta não localizada."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def substituir_guia(bot: WebBot, conta: str, guia: str) -> None:
    """
    Acessa o menu clicando com o botão direito na linha da conta e seleciona a opção 'Substituir guia'.
    Args:
        bot: Objeto do navegador
        conta: Número da conta paciente para validar carregamento da tela
        guia: Número da guia a ser substituído

    Returns: None

    """

    mensagem_erro = "Falha ao substituir a guia da conta. "

    try:
        # Click com o botão direito na primeira linha da tabela de contas
        if not element_right_click(bot=bot, xpath=f"//div[span[text()='{conta}']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Conta não localizada."])

        # Clica na opção 'Substituir guia'
        if not element_click(bot=bot, xpath="//div[text()='Substituir guia']", tentativas=4):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Opção (substituir guia) não localizada."])

        # Aguarda a tela carregar
        if not element_set_text(bot=bot, xpath="//input[@name='NR_NOVA_GUIA']", text=guia):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Pop-up (Substituir guia) não localizado."])

        # Clica em 'Ok'
        element_click(bot=bot, xpath="//button[span[contains(text(),'OK')]]")

        # Valida se a guia foi substituída com sucesso
        for n in range(10):  # Verificar se a guia aparece na tabela
            if not element_wait_displayed(bot=bot, xpath=f"//span[text()='Substituir guia']", tentativas=1):
                return
            bot.wait(500)

        raise Exception(["Excecao_Sistema", mensagem_erro + "Não foi possível validar a substituição."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def substituir_senha(bot: WebBot, conta: str, senha: str, substituir_todas: bool = False) -> None:
    """
    Acessa o menu clicando com o botão direito na linha da conta e seleciona a opção 'Substituir senha'.
    Args:
        bot: Objeto do Navegador
        conta: Número da conta paciente para validação de carregamento da tela
        senha: Nova Senha a ser substituída
        substituir_todas: Flegar o checkbox 'Substituir todas'?

    Returns: None

    """
    mensagem_erro = "Falha ao substituir a senha da conta. "
    try:
        # Click com o botão direito na linha da conta
        if not element_right_click(bot=bot, xpath=f"//div[span[text()='{conta}']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Conta não localizada."])

        # Clica na opção 'Substituir senha'
        if not element_click(bot=bot, xpath="//div[text()='Substituir senha']", tentativas=4):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Opção (Substituir senha) não localizada."])

        # Aguarda pop-up 'Substituir senha' carregar
        if not element_wait_displayed(bot=bot, xpath="//input[@name='DS_NOVA_SENHA']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Pop-up (Substituir senha) não localizado."])

        # Flega o check-box 'Substituir todas'
        if substituir_todas:
            if not element_click(bot=bot, xpath="//div[input[@name='IE_SUBSTITUIR']]"):
                raise Exception(["Excecao_Sistema", mensagem_erro + "Checkbox (Substituir todas) não localizado."])
        else:
            # Insere a Senha
            element_set_text(bot=bot, xpath="//input[@name='DS_SENHA']", text=senha)
            bot.tab()

        # Insere a Nova Senha
        element_set_text(bot=bot, xpath="//input[@name='DS_NOVA_SENHA']", text=senha)
        bot.tab()

        # Clica em 'Ok'
        if not element_click(bot=bot, xpath="//button[span[contains(text(),'OK')]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        # Valida se a senha foi substituída com sucesso
        for n in range(10):  # Verificar se a senha aparece na tabela
            if not element_wait_displayed(bot=bot, xpath=f"//span[text()='Substituir senha']", tentativas=1):
                return
            bot.wait(500)

        raise Exception(["Excecao_Sistema", mensagem_erro + "Não foi possível validar a substituição."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def recalcular_conta(bot: WebBot, conta: str) -> None:
    """
    Acessa o menu clicando com o botão direito na linha da conta, e seleciona a opção recalcular conta.
    Args:
        bot: Objeto do navegador
        conta: Número da conta paciente
    Returns: None
    """
    mensagem_erro = "Falha ao recalcular a conta do paciente. "
    try:
        # Click com o botão direito na linha da conta
        if not element_right_click(bot=bot, xpath=f"//div[span[text()='{conta}']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Conta não localizada."])

        # Clicar em 'Recalcular conta'
        if not element_click(bot=bot, xpath="//div[text()='Recalcular conta']", tentativas=4):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Opção (Recalcular conta) não localizada."])

        # Aguardar o pop-up de confirmação
        xpath = "//div[text()='Conta atualizada com sucesso!']"
        if not bot.find_element(xpath, By.XPATH, 15000, ensure_visible=True):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Pop-up de confirmação não localizado."])

        # Clica em 'Ok'
        if not element_click(bot=bot, xpath="//button[span[contains(text(),'OK')]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        # Valida se retornou para a tela inicial
        for n in range(10):
            if not element_wait_displayed(bot=bot, xpath="//div[text()='Conta atualizada com sucesso!']", tentativas=1):
                return
            bot.wait(500)

        raise Exception(["Excecao_Sistema", mensagem_erro + "Não foi possível validar a atualização."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def atualizar_conta_tiss(bot: WebBot, conta: str) -> None:
    """
    Acessa o menu clicando com o botão direito na linha da conta e seleciona a opção 'Atualizar conta TISS'.
    Args:
        bot: Objeto do navegador
        conta: Número da conta paciente para validação de carregamento da tela
    Returns: None
    """
    mensagem_erro = "Falha ao atualizar a conta TISS. "
    try:
        # Click com o botão direito na linha da conta
        if not element_right_click(bot=bot, xpath=f"//div[span[text()='{conta}']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Conta não localizada."])

        # Clica na opção 'Atualizar conta TISS'
        if not element_click(bot=bot, xpath="//div[text()='Atualizar conta TISS']", tentativas=4):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Opção (Atualizar conta TISS) não localizada."])

        # Aguarda pop-up de confirmação
        if not element_wait_displayed(bot=bot, xpath="//div[text()='Conta atualizada com sucesso!']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Pop-up de confirmação não localizado."])

        # Clica em 'Ok'
        if not element_click(bot=bot, xpath="//button[text()='Ok']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        # Valida se retornou para a tela inicial
        for n in range(10):
            if not element_wait_displayed(bot=bot, xpath="//div[text()='Conta atualizada com sucesso!']", tentativas=1):
                return
            bot.wait(500)

        raise Exception(["Excecao_Sistema", mensagem_erro + "Não foi possível validar a atualização."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def fechar_atendimento(bot: WebBot, conta: str) -> None:
    """
    Clica com o botão direito na linha da conta, seleciona a opção fechar atendimento e verifica se há inconsistência.
    Args:
        bot: Objeto do navegador
        conta: Número da conta paciente para validação de carregamento da tela
    Returns: None
    """
    mensagem_erro = "Falha ao mudar status da conta. "
    try:
        # Click com o botão direito na linha da conta
        if not element_right_click(bot=bot, xpath=f"//div[span[text()='{conta}']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Conta não localizada."])

        # Clica na opção 'Fechar atendimento'
        if not element_click(bot=bot, xpath="//div[text()='Fechar atendimento']", tentativas=4):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Opção (Fechar atendimento) não localizada."])

        # Aguardar o pop-up de confirmação
        xpath = fr"//div[text()='Confirma o final do atendimento?']"
        if not bot.find_element(xpath, By.XPATH, ensure_visible=True):
            raise Exception(["Excecao_Sistema", "Pop-up de confirmação não localizado."])

        # Clica em 'Ok'
        if not element_click(bot=bot, xpath="//button[text()='Ok']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        # Aguardar o popup de 'Consistência' (demora bastante)
        xpath = fr"//div[@title='Consistência']"
        if not bot.find_element(xpath, By.XPATH, ensure_visible=True, waiting_time=60000):
            raise Exception(["Excecao_Sistema", "Popup (Consistência) não localizada."])

        # Verificar se possuí alguma inconsistência na tabela de Consistências
        inconsistencia = verificar_tabela_consistencia(bot=bot)
        if inconsistencia:
            raise Exception(["Excecao_Sistema", mensagem_erro + inconsistencia])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def mudar_status_conta(bot: WebBot, conta) -> None:
    """
    Clica com o botão direito na linha da conta e seleciona a opção 'Muda status conta'.
    Args:
        bot: Objeto do navegador
        conta: Número da conta paciente para validação de carregamento da tela
    Returns: None
    """

    mensagem_erro = "Falha ao mudar o status da conta. "

    try:
        # Click com o botão direito na linha da conta
        if not element_right_click(bot=bot, xpath=f"//div[span[text()='{conta}']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Conta não localizada."])

        # Clica na opção 'Muda status conta'
        if not element_click(bot=bot, xpath="//div[text()='Muda status conta']", tentativas=4):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Opção (Muda status conta) não localizada."])

        # Verificar se aparece o pop-up de inconsistência
        # ToDo: Analisar esse popup
        if element_wait_displayed(bot=bot, xpath="//div[contains(text(),'Inconsistências')]", tentativas=6):
            raise Exception(["Excecao_Negocio", "Tipo de saída da guia de consulta não informado."])

        # Aguardar o popup de 'Consistência' (demora bastante)
        xpath = "//div[@title='Consistência']"
        if not bot.find_element(xpath, By.XPATH, ensure_visible=True, waiting_time=60000):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Popup (Consistência) não localizada."])

        # Verificar se possuí alguma inconsistência na tabela de Consistências
        incosistencia = verificar_tabela_consistencia(bot=bot)

        # Clica em 'Ok'
        xpath = "//div[@class='region-cel' and //div[@title='Consistência']]//button[span[text()='OK']]"
        if not element_click(bot=bot, xpath=xpath):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        if incosistencia:
            # Duplo click na linha referente a conta
            acessar_conta(bot=bot, conta=conta)

            # Adicionar etapa na conta
            adicionar_etapa(bot=bot, etapa="RPA", observacoes=incosistencia)

            # Reportar exceção de negócio
            raise Exception(["Excecao_Negocio", mensagem_erro + incosistencia])

        # Valida se retornou para a tela inicial
        for n in range(10):
            if not element_wait_displayed(bot=bot, xpath="//div[@title='Consistência']", tentativas=1):
                return
            bot.wait(500)

        raise Exception(["Excecao_Sistema", mensagem_erro + "Não foi possível validar a mudança."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def inserir_conta_protocolo(bot: WebBot, identificador_protocolo: str) -> None:
    """
    Função insere a conta em um protocolo
    Args:
        bot: Objeto do navegador
        identificador_protocolo: Identificador do protocolo a ser atribuído a conta
    Returns: None
    """

    mensagem_erro = "Falha ao inserir a conta no protocolo. "

    try:
        # Aguarda o carregamento do pop-up de inserir no protocolo
        if not element_wait_displayed(bot=bot, xpath="//span[text()='Inserir no protocolo']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Pop-up (Inserir no protocolo) não localizado."])

        # Preencher o campo 'Nome'
        element_click(bot=bot, xpath="//div[input[@name='NR_PROTOCOLO']]", delay=1000)
        if not element_click(bot=bot, xpath=f"//a[span[contains(text(),'{identificador_protocolo}')]]", delay=250):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Protocolo não localizado."])

        # Clica em 'Ok'
        if not element_click(bot=bot, xpath="//button[span[contains(text(),'OK')]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        # Após clicar em 'Ok', aparece um segundo popup de confirmação. Clica em 'Ok' novamente
        if not element_click(bot=bot, xpath="//button[text()='Ok']"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Pop-up de Confirmação não foi localizado."])

        # A conta foi inserida com sucesso se aparecer o popup 'Atenção' com a quantidade de contas no protocolo
        if element_wait_displayed(bot=bot, xpath="//div[text()='Atenção']"):
            # Clica em 'Ok'
            element_click(bot=bot, xpath="//button[text()='Ok']")
            return

        # Verificar se aparece o popup de 'Operação abortada'
        if element_wait_displayed(bot=bot, xpath="//div[text()='Operação abortada']", tentativas=4):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro += element_get_text(bot=bot, xpath=xpath)

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def verificar_tabela_consistencia(bot: WebBot) -> str:
    """
    Função faz um loop pela tabela de consistência para verificar se possuí alguma inconsistência.
    Args:
        bot: Objeto do navegador
    Returns: Inconsistência encontrada
    """

    mensagem_erro = "Falha ao verificar tabela de consistências. "

    try:
        # Pega a quantidade de linhas na tabela de consistências
        xpath = "//div[div[div[div[div[span[text()='Consistência']]]]]]//i[@id='totalRecordsPageFinish']"
        qt_registros = element_get_text(bot=bot, xpath=xpath)
        qt_registros = int(re.sub(r"[^0-9]", "", qt_registros)) + 1

        # Xpath tabela
        xpath_tabela = "//div[contains(@ng-repeat,'rowContainer')]"

        # Loop pela tabela de Consistências do tasy
        for num_linha in range(1, qt_registros):

            # 5 = Coluna 'FC'
            num_coluna = 5

            # Pega o valor da coluna 'FC'
            xpath = f"({xpath_tabela})[{num_linha}]/div/div/div[{num_coluna}]"
            fc = bot.find_element(xpath, By.XPATH, ensure_visible=True).text

            # Reportar o erro se o valor da coluna 'FC' for diferente de 'Sim'
            if fc != 'Sim':
                #  2 = Coluna 'Inconsistência'
                num_coluna = 2

                # Pega o valor da coluna 'Inconsistência'
                xpath = f"({xpath_tabela})[{num_linha}]/div/div/div[{num_coluna}]"
                inconsistencia = bot.find_element(xpath, By.XPATH, ensure_visible=True).text

                # Reportar a inconsistência
                return inconsistencia

        return ""

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def adicionar_etapa(bot: WebBot, etapa: str, observacoes: str) -> None:
    """
    Adiciona uma nova etapa á conta.
    Args:
        bot: Objeto do Navegador
        etapa: Nome da etapa a ser inserida
        observacoes: Mensagem á ser adiciona no campo 'Observações'.
    Returns: None
    """
    mensagem_erro = "Falha ao adicionar etapa na conta do paciente. "
    try:
        # Clica na aba 'Etapa conta'
        if not element_click(bot=bot, xpath="//div[span[text()='Etapas conta']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Menu (Etapas conta) não localizado."])

        # Clica no botão 'Adicionar'
        if not element_click(bot=bot, xpath="//*[span[text()='Adicionar']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Adicionar) não foi localizado."])

        # Preenche o campo 'Etapa'
        element_click(bot=bot, xpath="//div[input[@name='NR_SEQ_ETAPA']]")
        if not element_click(bot=bot, xpath=f"//a[span[contains(text(),'{etapa}')]]", delay=250):
            raise Exception(["Excecao_Sistema", mensagem_erro + f"Etapa ({etapa}) não localizada."])

        # Preenche o campo 'Observações'
        element_set_text(bot=bot, xpath="//*[@name='DS_OBSERVACAO']", text=observacoes)
        bot.tab()

        # Clica no botão 'Salvar'
        if not element_left_click(bot=bot, xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Salvar) não localizado."])

        # Verificar se salvou com sucesso
        xpath = "//div[div[span[contains(text(),'Setor')]] and div[span[text()='Básica']]]"
        if element_wait_displayed(bot=bot, xpath=xpath):
            return

        # Verificar se aparece o popup de 'Operação abortada'
        if element_wait_displayed(bot=bot, xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro += element_get_text(bot=bot, xpath=xpath)

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def adicionar_conta(bot: WebBot, convenio: str, categoria: str = '', categoria_calculo: str = '') -> str:
    """
    Adiciona uma nova conta na função 'Conta Paciente' do Tasy.
    :param bot: Objeto da BotCity.
    :param convenio:
    :param categoria:
    :param categoria_calculo:
    :return: Número da conta criada.
    """

    mensagem_erro = "Falha ao adicionar uma nova conta na função Conta Paciente. "
    try:
        # Clica em 'Adicionar'
        if not element_click(bot=bot, xpath="//*[contains(text(),'Adicionar')]", delay=1000):
            raise Exception(["Excecao_Sistema", mensagem_erro + f"Botão (Adicionar) não localizado."])

        # Pega a nova conta
        conta = element_get_value(bot=bot, xpath="//input[@name='NR_INTERNO_CONTA']")
        # conta = ""
        # for n in range(20):
        #     conta = element_get_value(bot=bot, xpath="//input[@name='NR_INTERNO_CONTA']")
        #     if conta != "":
        #         break
        #     bot.wait(500)
        # if conta == "":
        #     raise Exception(["Excecao_Sistema", error_manager + "Conta não gerada."])

        # Preenche o campo 'Convênio'
        convenio_atual = element_get_text(bot=bot, xpath="//div[input[@name='CD_CONVENIO_PARAMETRO']]")
        if convenio != convenio_atual:
            element_click(bot=bot, xpath="//div[input[@name='CD_CONVENIO_PARAMETRO']]")
            if not element_click(bot=bot, xpath=f"//a[span[contains(text(),'{convenio}')]]", delay=250):
                raise Exception(["Excecao_Sistema", mensagem_erro + f"Convênio ({convenio}) não localizado."])

        # Preenche o campo 'Categoria'
        categoria_atual = element_get_text(bot=bot, xpath="//div[input[@name='CD_CATEGORIA_PARAMETRO']]")
        if categoria != "" and categoria != categoria_atual:
            element_click(bot=bot, xpath="//div[input[@name='CD_CATEGORIA_PARAMETRO']]")
            if not element_click(bot=bot, xpath=f"//a[span[contains(text(),'{categoria}')]]", delay=250):
                raise Exception(["Excecao_Sistema", mensagem_erro + f"Categoria ({categoria}) não localizada."])

        # Preenche o campo 'Categoria cálculo'
        categoria_calculo_atual = element_get_text(bot=bot, xpath="//div[input[@name='CD_CATEGORIA_CALCULO']]")
        if categoria_calculo != "" and categoria_calculo != categoria_calculo_atual:
            element_click(bot=bot, xpath="//div[input[@name='CD_CATEGORIA_CALCULO']]")
            if not element_click(bot=bot, xpath=f"//a[span[contains(text(),'{categoria_calculo}')]]", delay=250):
                raise Exception(["Excecao_Sistema", mensagem_erro + f"Categoria cálculo ({categoria_calculo}) não localizada."])

        # Clica no botão 'Salvar'
        if not element_click(bot=bot, xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Salvar) não localizado."])

        # Verificar se a conta criada aparece na tabela de contas
        if element_wait_displayed(bot=bot, xpath=f"//span[text()='{conta}']", tentativas=20):
            return conta

        # Verificar se aparece o popup de 'Operação abortada'
        if element_wait_displayed(bot=bot, xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro += element_get_text(bot=bot, xpath=xpath)

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def adicionar_taxa(bot: WebBot,
                   procedimento: str,
                   quantidade: str,
                   motivo_inclusao: str,
                   data_procedimento: str = None) -> None:
    """
    Adicionar uma nova taxa na conta do paciente.
    :param: bot: Objeto do Navegador.
    :param: conta: Conta do paciente.
    """
    mensagem_erro = "Falha ao adicionar taxa na conta. "

    try:
        # Acessar a aba 'Taxa'
        if not element_click(bot=bot, xpath="//div[span[text()='Taxa']]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Aba (Taxa) não localizada."])

        # Clica em 'Adicionar'
        if not element_click(bot=bot, xpath="//*[contains(text(),'Adicionar')]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Adicionar) não localizado."])

        # Pega a sequência da taxa
        sequencia = element_get_value(bot=bot, xpath="//input[@name='NR_SEQUENCIA']")
        # bot.wait(1000)

        # Preenche o campo 'Procedimento'
        element_set_text(bot=bot, xpath="//input[@name='NR_SEQ_PROC_INTERNO']", text=procedimento, delay=1000)
        cd_procedimento = ""
        for n in range(10):
            cd_procedimento = element_get_value(bot=bot, xpath="//input[@name='CD_PROCEDIMENTO']", tentativas=1)
            if cd_procedimento != "":
                break
            if element_wait_displayed(bot=bot, xpath="//div[contains(text(),'Informação')]", tentativas=2):
                xpath = "//div[div[div[div[contains(text(),'Informação')]]]]/div[2]/div"
                mensagem_erro += element_get_text(bot=bot, xpath=xpath)
                raise Exception(["Excecao_Sistema", mensagem_erro])
            bot.wait(500)
        if cd_procedimento == "":
            raise Exception(["Excecao_Sistema", mensagem_erro + "Procedimento não localizado."])

        # Preenche o campo 'Quantidade'
        element_set_text(bot=bot, xpath="//input[@name='QT_PROCEDIMENTO']", text=quantidade)
        bot.tab()

        # Preenche o campo 'Data procedimento'
        if data_procedimento:
            element_set_text(bot=bot, xpath="//input[@name='DT_PROCEDIMENTO']", text=data_procedimento)
            bot.tab()

        # Clica no botão 'Salvar'
        if not element_click(bot=bot, xpath="//div[div[div[span[text()='Salvar']]]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (Salvar) não localizado."])

        # No popup que aparece preenche o 'Motivo de inclusão'
        element_click(bot=bot, xpath="//div[input[@name='NR_SEQ_MOTIVO_INCL']]", delay=1000)
        if not element_click(bot=bot, xpath=f"//a[span[contains(text(),'{motivo_inclusao}')]]", delay=250):
            raise Exception(["Excecao_Sistema", mensagem_erro + f"Motivo de inclusão ({motivo_inclusao}) não localizado."])

        # Clica no botão 'Ok'
        if not element_click(bot=bot, xpath="//button[span[contains(text(),'OK')]]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        # Verifica se o pop-up de 'Consistência' aparece
        xpath = "//div[@title='Consistência']"
        if bot.find_element(xpath, By.XPATH, ensure_visible=True, waiting_time=3000):
            inconsistencia = verificar_tabela_consistencia(bot=bot)
            if inconsistencia:
                raise Exception(["Excecao_Sistema", mensagem_erro + inconsistencia])
            # Clica em 'Ok'
            if not element_click(bot=bot, xpath="//button[span[contains(text(),'OK')]]"):
                raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])

        # Verificar se a taxa criada aparece na tabela de taxas
        # if element_wait_displayed(bot=bot, xpath=f"//div[span[text()='{sequencia}']]"):
        #     return
        if confirmar_taxa_adicionada(nr_sequencia=sequencia):
            # Às vezes aparece um pop-up de "Informação". Clica em 'Ok'
            if element_wait_displayed(bot=bot, xpath="//div[contains(text(),'Informação')]", tentativas=4):
                if not element_click(bot=bot, xpath="//button[contains(text(),'Ok')]"):
                    raise Exception(["Excecao_Sistema", mensagem_erro + "Botão (OK) não localizado."])
            return

        # Verificar se aparece o popup de 'Operação abortada'
        if element_wait_displayed(bot=bot, xpath="//div[text()='Operação abortada']", tentativas=1):
            xpath = "//div[div[div[div[text()='Operação abortada']]]]/div[2]/div"
            mensagem_erro += element_get_text(bot=bot, xpath=xpath)

        raise Exception(["Excecao_Sistema", mensagem_erro])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def retornar_tela_contas(bot: WebBot) -> None:
    """
    Retornar para a tela de contas clicando no nome 'Conta:' que fica no canto superior esquerdo da tela.
    :param: bot: Objeto do Navegador.
    """
    mensagem_erro = "Falha ao retornar para a tela de contas. "

    try:
        # Clica para ativar a linha da canta na tabela.
        element_click(bot=bot, xpath="//div[div[text()='Conta']]", tentativas=4)

        # Valido carregamento da tela de detalhes da conta
        if not element_wait_displayed(bot=bot, xpath="//div[contains(text(),'Contas')]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Tela de contas não localizada."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)


def anexar_arquivo_conta(bot: WebBot, dir_arquivo: str) -> None:
    """
    Realiza o upload do arquivo na aba Anexo da conta.
    :param: bot: Objeto do Navegador.
    """
    mensagem_erro = "Falha ao anexas arquivo na conta. "

    try:
        # Clica para ativar a linha da canta na tabela.
        element_click(bot=bot, xpath="//div[div[text()='Conta']]", tentativas=4)

        # Valido carregamento da tela de detalhes da conta
        if not element_wait_displayed(bot=bot, xpath="//div[contains(text(),'Contas')]"):
            raise Exception(["Excecao_Sistema", mensagem_erro + "Tela de contas não localizada."])

    except Exception:
        error_message = salvar_log_erro(sys, mensagem_erro, bot)
        raise ValueError(error_message)

