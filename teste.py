from onco_packages.tasy.autorizacao_convenio import AutorizacaoConvenio
from onco_packages.tasy.tasy import Tasy


tasy = Tasy()
tasy.login()
ac = AutorizacaoConvenio(driver=tasy.driver)
ac.pesquisar_sequencia_autorizacao(seq_autorizacao="")
print("Hello world!!!")
