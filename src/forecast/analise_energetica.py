import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.modulos import Missao_espacial


class AnaliseEnergetica:
    '''
    Faz a analise dos dados de energia da missao.
    Calcula medias, identifica picos e verifica se a geracao
    esta conseguindo cobrir a demanda ao longo dos ciclos.
    '''

    def __init__(self, missao: Missao_espacial):
        self.missao = missao

    def _calcular_media(self, lista: list) -> float:
        '''Calcula a media aritmetica de uma lista. Retorna 0 se a lista estiver vazia.'''
        if not lista:
            return 0.0
        return sum(lista) / len(lista)

    def _calcular_minimo(self, lista: list) -> float:
        '''Retorna o menor valor da lista.'''
        if not lista:
            return 0.0
        minimo = lista[0]
        for valor in lista:
            if valor < minimo:
                minimo = valor
        return minimo

    def _calcular_maximo(self, lista: list) -> float:
        '''Retorna o maior valor da lista.'''
        if not lista:
            return 0.0
        maximo = lista[0]
        for valor in lista:
            if valor > maximo:
                maximo = valor
        return maximo

    def calcular_estatisticas_gerais(self) -> dict:
        '''
        Percorre a matriz de telemetria e calcula as principais
        estatisticas energeticas da missao.
        Retorna um dicionario com os resultados.
        '''
        matriz = self.missao.gerar_matriz_telemetria()

        if len(matriz) < 2:
            print("[ANALISE] Sem dados suficientes para analisar.")
            return {}

        # Extrai as colunas ignorando o cabecalho
        geracoes_totais = [linha[1] for linha in matriz[1:]]
        consumos = [linha[2] for linha in matriz[1:]]
        baterias = [linha[3] for linha in matriz[1:]]

        # Calcula o balanco energetico de cada ciclo (geracao - consumo)
        balancos = [geracoes_totais[i] - consumos[i] for i in range(len(geracoes_totais))]

        # Conta quantos ciclos tiveram deficit (consumiu mais do que gerou)
        ciclos_com_deficit = sum(1 for b in balancos if b < 0)

        estatisticas = {
            'total_ciclos': len(geracoes_totais),

            'geracao_media_W': self._calcular_media(geracoes_totais),
            'geracao_maxima_W': self._calcular_maximo(geracoes_totais),
            'geracao_minima_W': self._calcular_minimo(geracoes_totais),

            'consumo_medio_W': self._calcular_media(consumos),
            'consumo_maximo_W': self._calcular_maximo(consumos),
            'consumo_minimo_W': self._calcular_minimo(consumos),

            'bateria_media_pct': self._calcular_media(baterias),
            'bateria_minima_pct': self._calcular_minimo(baterias),
            'bateria_maxima_pct': self._calcular_maximo(baterias),

            'balanco_medio_W': self._calcular_media(balancos),
            'ciclos_com_deficit': ciclos_com_deficit,
            'porcentagem_deficit': (ciclos_com_deficit / len(balancos)) * 100
        }

        return estatisticas

    def verificar_eficiencia_geracao(self) -> str:
        '''
        Compara a geracao media com o consumo medio e retorna
        um diagnostico simples sobre a eficiencia energetica da missao.
        '''
        matriz = self.missao.gerar_matriz_telemetria()

        if len(matriz) < 2:
            return "Sem dados suficientes."

        geracoes = [linha[1] for linha in matriz[1:]]
        consumos = [linha[2] for linha in matriz[1:]]

        media_geracao = self._calcular_media(geracoes)
        media_consumo = self._calcular_media(consumos)

        if media_geracao == 0:
            return "CRITICO: Nenhuma geracao registrada!"

        # Calcula a porcentagem de cobertura
        cobertura = (media_geracao / media_consumo) * 100

        if cobertura >= 110:
            diagnostico = f"OTIMO: Geracao cobre {cobertura:.1f}% do consumo. Ha margem de seguranca."
        elif cobertura >= 90:
            diagnostico = f"ADEQUADO: Geracao cobre {cobertura:.1f}% do consumo. Equilibrio razoavel."
        elif cobertura >= 70:
            diagnostico = f"ATENCAO: Geracao cobre apenas {cobertura:.1f}% do consumo. Bateria sendo usada."
        else:
            diagnostico = f"CRITICO: Geracao cobre somente {cobertura:.1f}% do consumo! Risco de colapso energetico."

        return diagnostico

    def encontrar_pior_ciclo(self) -> dict:
        '''
        Varre os dados e encontra o ciclo com o pior balanco energetico
        (maior diferenca entre consumo e geracao).
        '''
        matriz = self.missao.gerar_matriz_telemetria()

        if len(matriz) < 2:
            return {}

        pior_ciclo = 0
        pior_balanco = 0.0

        for linha in matriz[1:]:
            ciclo = linha[0]
            geracao = linha[1]
            consumo = linha[2]
            balanco = geracao - consumo

            if balanco < pior_balanco:
                pior_balanco = balanco
                pior_ciclo = ciclo

        return {
            'ciclo': pior_ciclo,
            'deficit_W': abs(pior_balanco)
        }

    def exibir_relatorio_energetico(self):
        '''
        Metodo principal que o Bruno pode chamar no menu.
        Mostra um relatorio completo e formatado da situacao energetica.
        '''
        print("\n" + "=" * 55)
        print("         RELATORIO DE ANALISE ENERGETICA")
        print("=" * 55)

        stats = self.calcular_estatisticas_gerais()

        if not stats:
            print("[ANALISE] Nao foi possivel gerar o relatorio.")
            print("=" * 55)
            return

        print(f"\n RESUMO GERAL ({stats['total_ciclos']} ciclos analisados)")
        print(f" {'-' * 45}")

        print(f"\n [GERACAO]")
        print(f"   Media  : {stats['geracao_media_W']:>10.2f} W")
        print(f"   Maxima : {stats['geracao_maxima_W']:>10.2f} W")
        print(f"   Minima : {stats['geracao_minima_W']:>10.2f} W")

        print(f"\n [CONSUMO]")
        print(f"   Media  : {stats['consumo_medio_W']:>10.2f} W")
        print(f"   Maximo : {stats['consumo_maximo_W']:>10.2f} W")
        print(f"   Minimo : {stats['consumo_minimo_W']:>10.2f} W")

        print(f"\n [BATERIA]")
        print(f"   Media  : {stats['bateria_media_pct']:>9.1f}%")
        print(f"   Minima : {stats['bateria_minima_pct']:>9.1f}%")
        print(f"   Maxima : {stats['bateria_maxima_pct']:>9.1f}%")

        print(f"\n [BALANCO ENERGETICO]")
        balanco = stats['balanco_medio_W']
        sinal = "+" if balanco >= 0 else ""
        print(f"   Balanco medio : {sinal}{balanco:.2f} W por ciclo")
        print(f"   Ciclos c/ deficit : {stats['ciclos_com_deficit']} ({stats['porcentagem_deficit']:.1f}% do total)")

        # Pior ciclo
        pior = self.encontrar_pior_ciclo()
        if pior:
            print(f"\n [PIOR CICLO REGISTRADO]")
            print(f"   Ciclo {pior['ciclo']} com deficit de {pior['deficit_W']:.2f} W")

        # Diagnostico geral
        print(f"\n [DIAGNOSTICO]")
        print(f"   {self.verificar_eficiencia_geracao()}")

        print("=" * 55 + "\n")