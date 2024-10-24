from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
from anticaptchaofficial.recaptchav3proxyless import recaptchaV3Proxyless
from config import ANTI_CAPTCHA_KEY, LOG_EX_SISTEMA


def recaptcha_v2_proxyless(site_url: str, site_key: str) -> str:
    """
    Resolve o recaptcha V2 através da API da Anti Captcha
    :param site_url: URL do site cujo captcha será resolvido.
    :param site_key: Atributo 'data-sitekey' do elemento com ID = 'recaptcha-demo'
    :return: Token que deve ser usado no atributo innerHTML do elemento com ID = 'g-recaptcha-response'

    Documentação da API da Anti Captcha: https://anti-captcha.com/pt/apidoc
    """
    mensagem_erro = "Falha ao resolver o captcha. "

    solver = recaptchaV2Proxyless()  # Tipo de CAPTCHAR
    solver.set_verbose(0)  # 0: Não printa resposta 'Processando', 1: Printa a cada 3 segundos
    solver.set_key(ANTI_CAPTCHA_KEY)  # Setar a variável ANTI_CAPTCHA_KEY no config.py
    solver.set_website_url(site_url)
    solver.set_website_key(site_key)

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        # print("g-response: " + g_response)
        return g_response
    else:
        # print("task finished with error " + solver.error_code)
        # print("task finished with error " + solver.err_string)
        raise Exception(["Excecao_Sistema", mensagem_erro + solver.error_code + ":" + solver.err_string])


def recaptcha_v3_proxyless(site_url: str, site_key: str) -> str:
    """
    Resolve o recaptcha V3 através da API da Anti Captcha
    :param site_url: URL do site cujo captcha será resolvido.
    :param site_key: Atributo 'data-sitekey' do elemento com ID = 'recaptcha-demo'
    :return: Token que deve ser usado no atributo innerHTML do elemento com ID = 'g-recaptcha-response'

    Documentação da API da Anti Captcha: https://anti-captcha.com/pt/apidoc
    """
    mensagem_erro = "Falha ao resolver o captcha. "

    solver = recaptchaV3Proxyless()  # Tipo de CAPTCHAR
    solver.set_verbose(1)  # 0: Não printa resposta 'Processando', 1: Printa a cada 3 segundos
    solver.set_key(ANTI_CAPTCHA_KEY)  # Setar a variável ANTI_CAPTCHA_KEY no config.py
    solver.set_website_url(site_url)
    solver.set_website_key(site_key)
    solver.set_page_action("home_page")
    solver.set_min_score(0.9)

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        # print("g-response: " + g_response)
        return g_response
    else:
        # print("task finished with error " + solver.error_code)
        # print("task finished with error " + solver.err_string)
        raise Exception([LOG_EX_SISTEMA, mensagem_erro + solver.error_code + ":" + solver.err_string])
