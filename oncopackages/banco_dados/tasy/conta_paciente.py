from oncopackages.banco_dados.tasy.tasy import BancoDadosTasy
import time


class ContaPaciente(BancoDadosTasy):

    def confirmar_taxa_adicionada(self, nr_sequencia: str) -> bool:
        """
        Espera e confirma se a taxa/bundle/procedimento foi adicionada.
        :param nr_sequencia: Coluna 'NR_SEQUENCIA' da tabela 'TASY.PROCEDIMENTO_PACIENTE'.
        :return True se a taxa foi adicionada, False se a taxa não foi adicionada.
        """
        query = f"""
            SELECT * 
            FROM TASY.PROCEDIMENTO_PACIENTE
            WHERE NR_SEQUENCIA = :NR_SEQUENCIA
        """
        taxa_adicionada = False
        contador = 0
        while contador <= 10:
            # Executa a consulta no banco de dados
            self.cursor.execute(query, NR_SEQUENCIA=nr_sequencia)

            # Pega o resultado da consulta
            row = self.cursor.fetchone()
            if row:
                taxa_adicionada = True
                break
            contador += 1
            time.sleep(1)

        return taxa_adicionada
