import sys
import os

# Adiciona o caminho da pasta src para conseguir importar os modulos corretamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.modulos import Missao_espacial


class ModeloPrevisaoBateria:
    '''
    Calcula uma regressao linear simples (y = mx + b) para prever
    quando o nivel da bateria vai chegar num ponto critico.

    Usa so matematica pura, sem bibliotecas externas.
    Formulas utilizadas:
        m = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x ** 2)
        b = (soma_y - m * soma_x) / n
    '''

    def __init__(self, missao: Missao_espacial):
        self.missao = missao

        # Coeficientes da reta (ficam None ate o modelo ser treinado)
        self.inclinacao_m = None
        self.interceptacao_b = None

        # Guarda os dados que foram usados no treino
        self.ciclos_usados = 0

    def treinar(self):
        '''
        Pega a matriz de telemetria da missao e calcula os coeficientes
        da reta de regressao linear usando apenas somas e divisoes.
        Retorna True se deu certo, False se nao tinha dados suficientes.
        '''
        matriz = self.missao.gerar_matriz_telemetria()

        # Precisa de pelo menos 2 linhas de dados (fora o cabecalho)
        if len(matriz) < 3:
            print("[PREVISAO] Dados insuficientes para treinar o modelo.")
            return False

        # Extrai X (ciclos) e Y (nivel da bateria), pulando o cabecalho (linha 0)
        X = [linha[0] for linha in matriz[1:]]
        Y = [linha[3] for linha in matriz[1:]]

        n = len(X)
        self.ciclos_usados = n

        # Calcula as somas necessarias para a formula da regressao
        soma_x = sum(X)
        soma_y = sum(Y)
        soma_xy = sum(X[i] * Y[i] for i in range(n))
        soma_x2 = sum(x ** 2 for x in X)

        # Denominador da formula (nao pode ser zero)
        denominador = (n * soma_x2) - (soma_x ** 2)

        if denominador == 0:
            print("[PREVISAO] Erro no calculo: divisao por zero no denominador.")
            return False

        # Calcula a inclinacao (m) e interceptacao (b)
        self.inclinacao_m = (n * soma_xy - soma_x * soma_y) / denominador
        self.interceptacao_b = (soma_y - self.inclinacao_m * soma_x) / n

        print(f"[PREVISAO] Modelo treinado com {n} ciclos de telemetria.")
        print(f"[PREVISAO] Inclinacao (m): {self.inclinacao_m:.5f} | Interceptacao (b): {self.interceptacao_b:.2f}")

        return True

    def prever_nivel_bateria(self, ciclo_futuro: int) -> float:
        '''
        Dado um numero de ciclo futuro, retorna o nivel de bateria previsto.
        Precisa ter chamado treinar() antes.
        '''
        if self.inclinacao_m is None:
            print("[PREVISAO] Modelo ainda nao foi treinado. Chame treinar() primeiro.")
            return -1.0

        nivel_previsto = self.inclinacao_m * ciclo_futuro + self.interceptacao_b
        return nivel_previsto

    def prever_ciclo_colapso(self, limite_critico: float = 20.0) -> int:
        '''
        Calcula em qual ciclo futuro a bateria vai atingir o nivel critico.
        Resolve a equacao: limite_critico = m * ciclo + b
        Entao: ciclo = (limite_critico - b) / m

        Se a inclinacao for positiva ou zero, a bateria nao esta caindo,
        entao nao tem previsao de colapso.
        Retorna o numero do ciclo ou -1 se nao conseguir calcular.
        '''
        if self.inclinacao_m is None:
            print("[PREVISAO] Modelo ainda nao foi treinado. Chame treinar() primeiro.")
            return -1

        # Se a bateria esta subindo ou estavel, nao vai colapsar
        if self.inclinacao_m >= 0:
            print("[PREVISAO] Tendencia da bateria e estavel ou crescente. Sem risco de colapso detectado.")
            return -1

        # Descobre o ciclo onde a bateria atinge o limite
        ciclo_critico = (limite_critico - self.interceptacao_b) / self.inclinacao_m
        ciclo_critico = int(ciclo_critico)

        # So faz sentido se for no futuro
        ciclos_ate_o_fim = ciclo_critico - self.ciclos_usados
        if ciclos_ate_o_fim < 0:
            print(f"[PREVISAO] ATENCAO: A bateria JA deveria ter atingido {limite_critico}% ha {abs(ciclos_ate_o_fim)} ciclos atras!")
            print(f"[PREVISAO] Nivel atual provavelmente esta critico. Verifique os dados ao vivo.")
        else:
            print(f"[PREVISAO] A bateria deve atingir {limite_critico}% no ciclo {ciclo_critico}.")
            print(f"[PREVISAO] Faltam aproximadamente {ciclos_ate_o_fim} ciclos para o nivel critico.")

        return ciclo_critico

    def exibir_resultado_completo(self, limite_critico: float = 20.0):
        '''
        Metodo que o Bruno pode chamar no menu para mostrar o resultado
        completo da analise preditiva pro usuario.
        '''
        print("\n" + "=" * 55)
        print("       ANALISE PREDITIVA - NIVEL DA BATERIA")
        print("=" * 55)

        # Tenta treinar, se nao tiver dados, ja avisa
        sucesso = self.treinar()
        if not sucesso:
            print("[PREVISAO] Nao foi possivel gerar previsao.")
            print("=" * 55)
            return

        # Mostra a tendencia
        print(f"\n Ciclos analisados : {self.ciclos_usados}")
        print(f" Inclinacao (m)    : {self.inclinacao_m:.5f} por ciclo")
        print(f" Interceptacao (b) : {self.interceptacao_b:.2f}%")

        if self.inclinacao_m < 0:
            print(f"\n TENDENCIA: QUEDA ({self.inclinacao_m:.5f}% por ciclo)")
        elif self.inclinacao_m > 0:
            print(f"\n TENDENCIA: SUBIDA (+{self.inclinacao_m:.5f}% por ciclo)")
        else:
            print("\n TENDENCIA: ESTAVEL")

        # Previsao para os proximos ciclos
        print(f"\n --- Projecao para proximos ciclos ---")
        proximo = self.ciclos_usados
        for passo in [10, 50, 100]:
            ciclo_alvo = proximo + passo
            nivel = self.prever_nivel_bateria(ciclo_alvo)
            nivel_exibido = max(0.0, min(100.0, nivel))  # fica entre 0 e 100
            print(f"   Ciclo {ciclo_alvo:>4}: {nivel_exibido:.1f}%")

        # Previsao do colapso
        print(f"\n --- Previsao de colapso (limite: {limite_critico}%) ---")
        ciclo_colapso = self.prever_ciclo_colapso(limite_critico)
        if ciclo_colapso > 0:
            ciclos_restantes = ciclo_colapso - self.ciclos_usados
            if ciclos_restantes > 0:
                print(f"   Ciclo de risco   : {ciclo_colapso}")
                print(f"   Ciclos restantes : {ciclos_restantes}")
            else:
                print(f"   SITUACAO CRITICA: Bateria abaixo do limite!")
        else:
            print("   Sem previsao de colapso no horizonte atual.")

        print("=" * 55 + "\n")