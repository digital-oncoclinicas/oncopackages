from oncopackages.banco_dados.tasy.tasy import BancoDadosTasy
from oncopackages.banco_dados.rpa import BancoDadosRpa


class AutorizacaoConvenio(BancoDadosTasy):
    def __init__(self, bd_rpa: BancoDadosRpa):
        super().__init__(bd_rpa)
            
    def carteirinha(self, autorizacao: str) -> str:
        """
        Consultar a carteirinha do paciente no banco de dados do Tasy.
        :param autorizacao: Atributo NR_SEQUENCIA da tabela AUTORIZACAO_CONVENIO;
        :return: Carteirinha do paciênte.
        """
        mensagem_erro = "Falha ao pegar a carteirinha do paciente no banco de dados do Tasy. "
        try:    
            # Query SQL
            query = f"""
            SELECT NVL(
                        (SELECT CD_USUARIO_CONVENIO
                            FROM TASY.PACIENTE_SETOR_CONVENIO
                            WHERE NR_SEQ_PACIENTE = AC.NR_SEQ_PACIENTE_SETOR
                            ORDER BY DT_ATUALIZACAO DESC
                            FETCH FIRST 1 ROW ONLY),
                        (SELECT ACC.CD_USUARIO_CONVENIO
                            FROM TASY.ATENDIMENTO_PACIENTE AP
                            JOIN TASY.ATEND_CATEGORIA_CONVENIO ACC ON ACC.NR_ATENDIMENTO = AP.NR_ATENDIMENTO
                            WHERE AP.CD_PESSOA_FISICA = AC.CD_PESSOA_FISICA
                                AND ACC.CD_USUARIO_CONVENIO IS NOT NULL
                                AND AP.CD_ESTABELECIMENTO = AC.CD_ESTABELECIMENTO
                            ORDER BY AP.DT_ATUALIZACAO DESC
                            FETCH FIRST 1 ROW ONLY)
                        ) CARTEIRINHA
            FROM TASY.AUTORIZACAO_CONVENIO AC
            WHERE AC.NR_SEQUENCIA = {autorizacao}
            """
    
            # Executa a consulta no banco de dados
            self.cursor.execute(query)
    
            # Pega o resultado da consulta
            row = self.cursor.fetchone()
            if not row:
                raise Exception(["Excecao_Negocio", mensagem_erro + "Carteirinha não localizada."])
    
            return row[0]
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro)
            raise ValueError(error_message)
        
    def anexos(self, autorizacao: str) -> list:
        """
        Consultar os anexos da aba Anexos da função AUTORIZAÇÃO CONVÊNIO, via banco de dados do Tasy.
        :param autorizacao: Atributo NR_SEQUENCIA da tabela AUTORIZACAO_CONVENIO;
        :return: Lista contendo os links de download dos aquivos anexados no Tasy.
        """
        mensagem_erro = "Falha ao pegar os dados dos anexos no banco de dados do Tasy. "
    
        try:
            # Query SQL
            query = f"""SELECT DS_ARQUIVO  --UTL_URL.ESCAPE(DS_ARQUIVO) AS DS_ARQUIVO
                        FROM TASY.AUTORIZACAO_CONVENIO_ARQ
                        WHERE 1 = 1
                            AND DS_ARQUIVO NOT LIKE '%mbssistemas%'
                            AND NR_SEQUENCIA_AUTOR = {autorizacao}"""
    
            # Executa a consulta no banco de dados
            self.cursor.execute(query)
    
            # Pega o resultado da consulta
            rows = self.cursor.fetchall()
            if len(rows) == 0:
                raise Exception(["Excecao_Negocio", mensagem_erro + "Anexos não localizados."])
    
            arquivos = list()
            for row in rows:
                arquivos.append(row[0])
    
            return arquivos
    
        except:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro)
            raise ValueError(error_message)
    
    def solicitante(self, autorizacao: str) -> dict:
        """
        Consultar os dados do solicitante no banco de dados do Tasy.
        :param autorizacao: Atributo NR_SEQUENCIA da tabela AUTORIZACAO_CONVENIO;
        :return: Dicionário com as chaves nr_crm, uf_crm e nm_medico.
        """
        mensagem_erro = "Falha ao pegar os dados do solicitante no banco de dados do Tasy. "
        try:
            # Query SQL
            query = f"""SELECT DISTINCT
                             M.NR_CRM,
                             SUBSTR(NVL(M.UF_CRM, TASY.OBTER_COMPL_PF(PF.CD_PESSOA_FISICA,1,'UF')),1,2) UF_CRM,
                             PF.NM_PESSOA_FISICA
                             --SUBSTR(TASY.OBTER_CONSELHO_PROFISSIONAL(PF.NR_SEQ_CONSELHO,'S'),1,255) DS_CONSELHO
                        FROM TASY.PESSOA_FISICA PF
                            JOIN TASY.MEDICO M ON M.CD_PESSOA_FISICA = PF.CD_PESSOA_FISICA
                            JOIN TASY.AUTORIZACAO_CONVENIO AC ON AC.CD_MEDICO_SOLICITANTE = M.CD_PESSOA_FISICA
                        WHERE 1 = 1 
                            AND M.NR_CRM IS NOT NULL
                            AND SUBSTR(NVL(M.UF_CRM, TASY.OBTER_COMPL_PF(PF.CD_PESSOA_FISICA,1,'UF')),1,2) IS NOT NULL
                            AND AC.NR_SEQUENCIA = {autorizacao}"""
    
            # Executa a consulta no banco de dados
            self.cursor.execute(query)
    
            # Pega o resultado da consulta
            row = self.cursor.fetchone()
            if row is None:
                raise Exception(["Excecao_Negocio", mensagem_erro + "Dados não localizados."])
    
            return {"nr_crm": row[0], "uf_crm": row[1], "nm_medico": row[2]}
    
        except:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro)
            raise ValueError(error_message)
    
    def procedimentos(self, autorizacao: str):
        """
        Consultar procedimentos no banco de dados do Tasy.
        :param autorizacao: Atributo NR_SEQUENCIA da tabela AUTORIZACAO_CONVENIO;
        :return: Tabela com os atributos CD_PROCEDIMENTO e QT_SOLICITADA.
        """
        mensagem_erro = "Falha ao pegar os procedimentos no banco de dados do Tasy. "
        try:
            # Query SQL
            query = f"""
            SELECT
                CASE 
                    WHEN CD_PROCEDIMENTO_TUSS <> '0' AND CD_PROCEDIMENTO_TUSS IS NOT NULL THEN TO_CHAR(CD_PROCEDIMENTO_TUSS)
                    ELSE TO_CHAR(CD_PROCEDIMENTO_CONVENIO)
                END CD_PROCEDIMENTO, 
                QT_SOLICITADA
            FROM TASY.PROCEDIMENTO_AUTORIZADO
            WHERE 1 = 1
                AND CASE 
                        WHEN CD_PROCEDIMENTO_TUSS <> '0' AND CD_PROCEDIMENTO_TUSS IS NOT NULL THEN TO_CHAR(CD_PROCEDIMENTO_TUSS)
                        ELSE TO_CHAR(CD_PROCEDIMENTO_CONVENIO)
                    END IS NOT NULL
                AND QT_SOLICITADA IS NOT NULL
                AND NR_SEQUENCIA_AUTOR = {autorizacao}"""
    
            # Executa a consulta no banco de dados
            self.cursor.execute(query)
    
            # Pega o resultado da consulta
            rows = self.cursor.fetchall()
            if not rows:
                raise Exception(["Excecao_Negocio", mensagem_erro + "Procedimentos não localizados."])
    
            return rows
    
        except:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro)
            raise ValueError(error_message)
    
    def paciente(self, autorizacao: str) -> dict:
        """
        Consultar dados do paciênte no banco de dados do Tasy.
        :param autorizacao: Atributo NR_SEQUENCIA da tabela AUTORIZACAO_CONVENIO;
        :return: Dicionário com as chaves idade, sexo, peso, altura, superficie_corporal e cd_pessoa_fisica.
        """
        mensagem_erro = "Falha ao pegar os dados do paciênte no banco de dados do Tasy. "
        try:
            # Query SQL
            query = f"""SELECT
                            TASY.OBTER_IDADE(PF.DT_NASCIMENTO, NVL(PF.DT_OBITO,SYSDATE), 'A') IDADE, 
                            CASE PF.IE_SEXO
                                WHEN 'F' THEN 'Feminino'
                                ELSE 'Masculino'
                            END SEXO,
                            PS.QT_PESO PESO, 
                            PS.QT_ALTURA ALTURA,
                            ROUND(TASY.OBTER_SUPERFICIE_CORP_RED_PED(PS.QT_PESO, PS.QT_ALTURA, PS.QT_REDUTOR_SC, PS.CD_PESSOA_FISICA, PS.NM_USUARIO, PS.IE_FORMULA_SUP_CORPOREA), 2) SUP_CORPOREA,
                            PF.CD_PESSOA_FISICA
                        FROM TASY.PESSOA_FISICA PF 
                            JOIN TASY.AUTORIZACAO_CONVENIO AC ON AC.CD_PESSOA_FISICA = PF.CD_PESSOA_FISICA
                            JOIN TASY.PACIENTE_SETOR PS ON PS.NR_SEQ_PACIENTE = AC.NR_SEQ_PACIENTE_SETOR
                        WHERE 1 = 1
                            AND PF.IE_SEXO IS NOT NULL
                            AND PS.QT_PESO IS NOT NULL
                            AND PS.QT_ALTURA IS NOT NULL
                            AND AC.NR_SEQUENCIA = {autorizacao}"""
    
            # Executa a consulta no banco de dados
            self.cursor.execute(query)
    
            # Pega o resultado da consulta
            row = self.cursor.fetchone()
            if row is None:
                raise Exception(["Excecao_Negocio", mensagem_erro + "Dados não localizados."])
    
            return {"idade": row[0],
                    "sexo": row[1],
                    "peso": row[2],
                    "altura": row[3],
                    "superficie_corporal": row[4],
                    "cd_pessoa_fisica": row[5]}
    
        except:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro)
            raise ValueError(error_message)
    
    def procedimento_interno(self, procedimento: str):
        """
        Consultar o código do procedimento interno no banco de dados do Tasy.
        :param procedimento: Código do procedimento encontrado no site do convênio.
        :return Procedimento interno do Tasy.
        """
        mensagem_erro = "Falha ao pegar o procedimento interno no banco de dados do Tasy. "
        try:
            # Query SQL
            query = f"""
                SELECT NVL(
                            (SELECT NR_SEQ_PROC_INTERNO
                                FROM TASY.CONVERSAO_PROC_CONVENIO 
                                WHERE CD_PROC_CONVENIO = :CD_PROCEDIMENTO
                                ORDER BY DT_ATUALIZACAO DESC
                                FETCH FIRST 1 ROW ONLY), 
                            (SELECT NR_SEQ_PROC_INTERNO
                                FROM TASY.PROCEDIMENTO_AUTORIZADO
                                WHERE CD_PROCEDIMENTO = :CD_PROCEDIMENTO OR CD_PROCEDIMENTO_TUSS = :CD_PROCEDIMENTO
                                ORDER BY DT_ATUALIZACAO DESC
                                FETCH FIRST 1 ROW ONLY)
                        ) NR_SEQ_PROC_INTERNO
                FROM DUAL
                FETCH FIRST 1 ROW ONLY
            """
    
            # Executa a consulta no banco de dados
            self.cursor.execute(query, CD_PROCEDIMENTO=str(procedimento))
    
            # Pega o resultado da consulta
            row = self.cursor.fetchone()
            if row[0] is None:
                mensagem_erro = f"Procedimento interno ({procedimento}) não localizados no banco de dados do Tasy."
                raise Exception(["Excecao_Negocio", mensagem_erro])
    
            return row[0]
    
        except:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro)
            raise ValueError(error_message)
    
    def buscar_estagio(self, estabelecimento: str, tipo_estagio: str) -> str:
        """
        Esta função busca o estágio no banco de dados de acordo com o estabelecimento.
        :param estabelecimento: Estabelecimento
        :param tipo_estagio: Estagio a ser buscado. ex: Autorizado
        :return: Estagio
        """
        mensagem_erro = "Falha ao pesquisar o estágio no banco de dados do robô. "
        try:
            # Query para buscar o estagio no banco de dados
            query = f"""
                    SELECT [ESTAGIO] 
                    FROM [RPA].[AUTORIZACAO_CONVENIO_ESTAGIOS]
                    WHERE [ESTABELECIMENTO] = '{estabelecimento}' AND [TIPO_ESTAGIO] = '{tipo_estagio}'
                    """
    
            # Executando o comando
            self.cursor.execute(query)
    
            # Pega o resultado da consulta
            row = self.cursor.fetchone()
            if not row:
                mensagem_erro += f"Estabelecimento ({estabelecimento}) e/ou tipo do estágio ({tipo_estagio}) não localizados."
                raise Exception(["Excecao_Negocio", mensagem_erro])
    
            return row[0]
    
        except Exception:
            error_message = self.bd_rpa.salvar_log_erro(mensagem_erro)
            raise ValueError(error_message)
