import csv
import os

from modules.modulos import (
    Missao_espacial, Modulo,
    SistemaGeracaoSolar, SistemaGeracaoEolica, SistemaArmazenamentoEnergetico,
    SensorDemandaGlobal, SensorTemperaturaInterna, SensorTemperaturaExterna,
    SensorRadicao, SensorO2, SensorIntegridadeEstrutural
)
from rules.regras import MotorDeRegras
from rules.alertas import CentralDeAlertas
from forecast.previsao import ModeloPrevisaoBateria
from forecast.analise_energetica import AnaliseEnergetica

#  FUNÇÃO: monta a missão com todos os módulos e sensores
def criar_missao():
    missao = Missao_espacial()

    # 2. CRIAÇÃO DOS MÓDULOS PRINCIPAIS (6 Módulos obrigatórios pela rubrica)
    mod_energia       = Modulo('ENE-01', 'Módulo Energético', 'Controle de Energia', 5, consumo=50)
    mod_suporte       = Modulo('SUP-01', 'Módulo Suporte à Vida', 'Suporte Vital', 5, consumo=200)
    mod_comunicacao   = Modulo('COM-01', 'Módulo de Comunicação', 'Transmissão de Dados', 4, consumo=100)
    mod_habitat       = Modulo('HAB-01', 'Módulo Habitat', 'Alojamento da Tripulação', 3, consumo=150)
    mod_laboratorio   = Modulo('LAB-01', 'Módulo Laboratório', 'Pesquisa Científica', 3, consumo=300)
    mod_armazenamento = Modulo('ARM-01', 'Módulo de Armazenamento', 'Estoque de Suprimentos', 2, consumo=50)

    missao.adicionar_modulo(mod_energia)
    missao.adicionar_modulo(mod_suporte)
    missao.adicionar_modulo(mod_comunicacao)
    missao.adicionar_modulo(mod_habitat)
    missao.adicionar_modulo(mod_laboratorio)
    missao.adicionar_modulo(mod_armazenamento)

    # 3. CRIAÇÃO DOS SISTEMAS E SENSORES (Iniciando com valores zerados/padrão) (NÃO MEXER AQUI)
    solar   = SistemaGeracaoSolar('Solar-01',   capacidade_max_geracao=6000, geracao_atual=0.0)
    eolico  = SistemaGeracaoEolica('Eolico-01', capacidade_max_geracao=4000, geracao_atual=0.0)
    bateria = SistemaArmazenamentoEnergetico('Bateria-01', capacidade_max_armazenamento=100)

    sensor_demanda     = SensorDemandaGlobal('Sensor_Demanda_Total', 'Mede consumo global',    'W',   leitura_inicial=0.0)
    sensor_temp_int    = SensorTemperaturaInterna('Sensor_Temp_Int', 'Mede Temp Interna',      '°C',  leitura_inicial=22.0)
    sensor_temp_ext    = SensorTemperaturaExterna('Sensor_Temp_Ext', 'Mede Temp Externa',      '°C',  leitura_inicial=-50.0)
    sensor_radiacao    = SensorRadicao('Sensor_Radiacao',            'Mede Nível de Radiação', 'mSv', leitura_inicial=0.0)
    sensor_o2          = SensorO2('Sensor_O2_Principal',             'Mede Nível de Oxigênio', '%',   leitura_inicial=21.0)
    sensor_integridade = SensorIntegridadeEstrutural('Sensor_Integridade', 'Mede Saúde do Casco', '%', leitura_inicial=100.0)

    # 4.ACOPLAMENTO DO SISTEMA COM O MODULO, SEGUNDO MINHA HIERARQUIA DEFINIDA
    mod_energia.adicionar_sistema(solar)
    mod_energia.adicionar_sistema(eolico)
    mod_energia.adicionar_sistema(bateria)
    mod_energia.adicionar_sensor(sensor_demanda)

    mod_suporte.adicionar_sensor(sensor_temp_int)
    mod_suporte.adicionar_sensor(sensor_temp_ext)
    mod_suporte.adicionar_sensor(sensor_radiacao)
    mod_suporte.adicionar_sensor(sensor_o2)
    mod_suporte.adicionar_sensor(sensor_integridade)

    return missao

#  FUNÇÃO: injeta um conjunto de dados na missão
def injetar_dados(missao, solar_w, eolico_w, demanda_w, bateria_pct,
                  o2_pct, temp_int, temp_ext, radiacao, integridade):

    mod_energia = missao.modulos['ENE-01']
    mod_suporte = missao.modulos['SUP-01']

    mod_energia.sistemas['Solar-01'].atualizar_dados(solar_w, 0.0)
    mod_energia.sistemas['Eolico-01'].atualizar_dados(eolico_w, 0.0)
    mod_energia.sistemas['Bateria-01'].atualizar_dados(bateria_pct, 0.0)

    mod_energia.sensores['Sensor_Demanda_Total'].registrar_leitura(demanda_w)
    mod_suporte.sensores['Sensor_O2_Principal'].registrar_leitura(o2_pct)
    mod_suporte.sensores['Sensor_Temp_Int'].registrar_leitura(temp_int)
    mod_suporte.sensores['Sensor_Temp_Ext'].registrar_leitura(temp_ext)
    mod_suporte.sensores['Sensor_Radiacao'].registrar_leitura(radiacao)
    mod_suporte.sensores['Sensor_Integridade'].registrar_leitura(integridade)



#mostra os alertas que foram gerados
def mostrar_alertas(central):
    quantidade = central.obter_quantidade_alertas_pendentes()

    if quantidade == 0:
        print("Nenhum alerta gerado.")
        return

    print(f"\n{quantidade} alerta(s) encontrado(s):\n")

    while central.obter_quantidade_alertas_pendentes() > 0:
        alerta = central.processar_proximo_alerta()
        print(f"  [{alerta['severidade']}] {alerta['mensagem']}")
        print(f"  Recomendação: {alerta['recomendacao']}\n")

#  SIMULADOR DE CENÁRIOS
def simulador_de_cenarios():

    print("\n  Escolha um cenário:\n")
    print("  [1] Operação Normal        - Missão estável, tudo funcionando")
    print("  [2] Crise Energética       - Bateria baixa, solar e eólico falhando")
    print("  [3] Risco à Vida           - O2 baixo e temperatura interna crítica")
    print("  [4] Tempestade de Radiação - Radiação alta, solar comprometido")
    print("  [5] Degradação Estrutural  - Casco com integridade crítica")
    print("  [0] Voltar\n")

    opcao = input("  Opção: ").strip()

    if opcao == '0':
        return

    # Cada cenário é um conjunto fixo de valores
    if opcao == '1':
        nome = "Operacao Normal"
        solar_w     = 5500.0
        eolico_w    = 3800.0
        demanda_w   = 2800.0
        bateria_pct = 88.0
        o2_pct      = 21.0
        temp_int    = 22.0
        temp_ext    = -48.0
        radiacao    = 0.4
        integridade = 100.0

    elif opcao == '2':
        nome = "Crise Energetica"
        solar_w     = 200.0
        eolico_w    = 0.0
        demanda_w   = 3500.0
        bateria_pct = 18.0
        o2_pct      = 21.0
        temp_int    = 21.5
        temp_ext    = -55.0
        radiacao    = 0.3
        integridade = 100.0

    elif opcao == '3':
        nome = "Risco a Vida"
        solar_w     = 5000.0
        eolico_w    = 3000.0
        demanda_w   = 2500.0
        bateria_pct = 75.0
        o2_pct      = 17.5
        temp_int    = 12.0
        temp_ext    = -60.0
        radiacao    = 0.5
        integridade = 95.0

    elif opcao == '4':
        nome = "Tempestade de Radiacao"
        solar_w     = 1200.0
        eolico_w    = 3500.0
        demanda_w   = 3000.0
        bateria_pct = 55.0
        o2_pct      = 20.8
        temp_int    = 21.0
        temp_ext    = -40.0
        radiacao    = 2.8
        integridade = 68.0

    elif opcao == '5':
        nome = "Degradacao Estrutural"
        solar_w     = 4800.0
        eolico_w    = 3200.0
        demanda_w   = 2700.0
        bateria_pct = 82.0
        o2_pct      = 21.0
        temp_int    = 22.0
        temp_ext    = -50.0
        radiacao    = 0.6
        integridade = 62.0

    else:
        print("  Opção inválida.")
        return

    print(f"\n  === Simulando: {nome} ===\n")

    missao  = criar_missao()
    central = CentralDeAlertas()
    motor   = MotorDeRegras(missao, central)

    injetar_dados(missao, solar_w, eolico_w, demanda_w, bateria_pct,
                  o2_pct, temp_int, temp_ext, radiacao, integridade)

    motor.analisar_status_geral()

    print(f"  Solar          : {solar_w} W")
    print(f"  Eólico         : {eolico_w} W")
    print(f"  Bateria        : {bateria_pct} %")
    print(f"  Demanda        : {demanda_w} W")
    print(f"  O2             : {o2_pct} %")
    print(f"  Temp. Interna  : {temp_int} °C")
    print(f"  Temp. Externa  : {temp_ext} °C")
    print(f"  Radiação       : {radiacao} mSv")
    print(f"  Integridade    : {integridade} %")

    print("\n  --- Alertas gerados ---")
    mostrar_alertas(central)


# ============================================================
#  TELEMETRIA — lê o CSV e processa os dados
# ============================================================
def telemetria_csv():
    print("\n  Carregando dados do CSV...\n")

    missao  = criar_missao()
    central = CentralDeAlertas()
    motor   = MotorDeRegras(missao, central)

    caminho = os.path.join(os.path.dirname(__file__), '..', 'data', 'dados.csv')
    ciclos  = 0

    try:
        with open(caminho, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                injetar_dados(
                    missao,
                    float(linha['Geracao_Solar_W']),
                    float(linha['Geracao_Eolica_W']),
                    float(linha['Demanda_Global_W']),
                    float(linha['Nivel_Bateria_Pct']),
                    float(linha['O2_Pct']),
                    float(linha['Temp_Int_C']),
                    float(linha['Temp_Ext_C']),
                    float(linha['Radiacao_mSv']),
                    float(linha['Integridade_Pct'])
                )
                motor.analisar_status_geral()
                ciclos += 1

        print(f"  {ciclos} ciclos carregados com sucesso.\n")

    except FileNotFoundError:
        print("  Erro: arquivo dados.csv não encontrado.")
        return

    matriz = missao.gerar_matriz_telemetria()
    print("  Últimos 5 ciclos registrados:\n")
    print(f"  {'Ciclo':>5}  {'Geração (W)':>12}  {'Consumo (W)':>12}  {'Bateria (%)':>11}")
    print("  " + "-" * 46)
    for linha in matriz[-5:]:
        print(f"  {linha[0]:>5}  {linha[1]:>12.1f}  {linha[2]:>12.1f}  {linha[3]:>11.1f}")

    print("\n  --- Alertas gerados durante a missão ---")
    mostrar_alertas(central)


# ============================================================
#  ANÁLISE ENERGÉTICA
# ============================================================
def analise_energetica():
    print("\n  Processando análise energética...\n")

    missao  = criar_missao()
    central = CentralDeAlertas()
    motor   = MotorDeRegras(missao, central)

    caminho = os.path.join(os.path.dirname(__file__), '..', 'data', 'dados.csv')

    try:
        with open(caminho, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                injetar_dados(
                    missao,
                    float(linha['Geracao_Solar_W']),
                    float(linha['Geracao_Eolica_W']),
                    float(linha['Demanda_Global_W']),
                    float(linha['Nivel_Bateria_Pct']),
                    float(linha['O2_Pct']),
                    float(linha['Temp_Int_C']),
                    float(linha['Temp_Ext_C']),
                    float(linha['Radiacao_mSv']),
                    float(linha['Integridade_Pct'])
                )
                motor.analisar_status_geral()
    except FileNotFoundError:
        print("  Erro: arquivo dados.csv não encontrado.")
        return

    analise = AnaliseEnergetica(missao)
    analise.exibir_relatorio_energetico()


# ============================================================
#  PREVISÃO DA BATERIA
# ============================================================
def previsao_bateria():
    print("\n  Treinando modelo de previsão...\n")

    missao  = criar_missao()
    central = CentralDeAlertas()
    motor   = MotorDeRegras(missao, central)

    caminho = os.path.join(os.path.dirname(__file__), '..', 'data', 'dados.csv')

    try:
        with open(caminho, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                injetar_dados(
                    missao,
                    float(linha['Geracao_Solar_W']),
                    float(linha['Geracao_Eolica_W']),
                    float(linha['Demanda_Global_W']),
                    float(linha['Nivel_Bateria_Pct']),
                    float(linha['O2_Pct']),
                    float(linha['Temp_Int_C']),
                    float(linha['Temp_Ext_C']),
                    float(linha['Radiacao_mSv']),
                    float(linha['Integridade_Pct'])
                )
                motor.analisar_status_geral()
    except FileNotFoundError:
        print("  Erro: arquivo dados.csv não encontrado.")
        return

    modelo = ModeloPrevisaoBateria(missao)
    modelo.exibir_resultado_completo(limite_critico=20.0)


# ============================================================
#  MENU PRINCIPAL
# ============================================================
def main():
    print("=" * 50)
    print("   ASTRO MONITOR - CENTRO DE CONTROLE")
    print("=" * 50)

    while True:
        print("\n  [1] Simulador de Cenários")
        print("  [2] Telemetria Completa (CSV)")
        print("  [3] Análise Energética")
        print("  [4] Previsão da Bateria")
        print("  [0] Sair\n")

        opcao = input("  Escolha uma opção: ").strip()

        if opcao == '1':
            simulador_de_cenarios()
        elif opcao == '2':
            telemetria_csv()
        elif opcao == '3':
            analise_energetica()
        elif opcao == '4':
            previsao_bateria()
        elif opcao == '0':
            print("\n  Sistema encerrado.\n")
            break
        else:
            print("\n  Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()