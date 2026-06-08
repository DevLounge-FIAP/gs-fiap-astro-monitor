import csv
import os

from modules.modulos import (
    Missao_espacial,
    Modulo,
    SistemaGeracaoSolar,
    SistemaGeracaoEolica,
    SistemaArmazenamentoEnergetico,
    SensorDemandaGlobal,
    SensorTemperaturaInterna,
    SensorTemperaturaExterna,
    SensorRadicao,
    SensorO2,
    SensorIntegridadeEstrutural,
)
from rules.alertas import CentralDeAlertas
from rules.regras import MotorDeRegras
from forecast.analise_energetica import AnaliseEnergetica
from forecast.previsao import ModeloPrevisaoBateria


def criar_missao():
    missao = Missao_espacial()

    mod_energia = Modulo('ENE-01', 'Modulo Energetico', 'Controle de Energia', 5, consumo=50)
    mod_suporte = Modulo('SUP-01', 'Modulo Suporte a Vida', 'Suporte Vital', 5, consumo=200)
    mod_comunicacao = Modulo('COM-01', 'Modulo Comunicacao', 'Transmissao', 4, consumo=100)
    mod_habitat = Modulo('HAB-01', 'Modulo Habitat', 'Alojamento', 3, consumo=150)
    mod_laboratorio = Modulo('LAB-01', 'Modulo Laboratorio', 'Pesquisa', 3, consumo=300)
    mod_armazenamento = Modulo('ARM-01', 'Modulo Armazenamento', 'Estoque', 2, consumo=50)

    missao.adicionar_modulo(mod_energia)
    missao.adicionar_modulo(mod_suporte)
    missao.adicionar_modulo(mod_comunicacao)
    missao.adicionar_modulo(mod_habitat)
    missao.adicionar_modulo(mod_laboratorio)
    missao.adicionar_modulo(mod_armazenamento)

    solar = SistemaGeracaoSolar('Solar-01', capacidade_max_geracao=6000, geracao_atual=0.0)
    eolico = SistemaGeracaoEolica('Eolico-01', capacidade_max_geracao=4000, geracao_atual=0.0)
    bateria = SistemaArmazenamentoEnergetico('Bateria-01', capacidade_max_armazenamento=100)

    sensor_demanda = SensorDemandaGlobal('Sensor_Demanda_Total', 'Mede consumo global', 'W', leitura_inicial=0.0)
    sensor_temp_int = SensorTemperaturaInterna('Sensor_Temp_Int', 'Mede Temp Interna', 'C', leitura_inicial=22.0)
    sensor_temp_ext = SensorTemperaturaExterna('Sensor_Temp_Ext', 'Mede Temp Externa', 'C', leitura_inicial=-50.0)
    sensor_radiacao = SensorRadicao('Sensor_Radiacao', 'Mede Nivel de Radiacao', 'mSv', leitura_inicial=0.0)
    sensor_o2 = SensorO2('Sensor_O2_Principal', 'Mede Nivel de Oxigenio', '%', leitura_inicial=21.0)
    sensor_integridade = SensorIntegridadeEstrutural('Sensor_Integridade', 'Mede Saude do Casco', '%', leitura_inicial=100.0)

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


def injetar_dados(missao, solar_w, eolico_w, demanda_w, bateria_pct, o2_pct, temp_int, temp_ext, radiacao, integridade):
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


def carregar_amostra_csv(missao, limite_linhas=50):
    caminho = os.path.join(os.path.dirname(__file__), '..', 'data', 'dados.csv')

    with open(caminho, mode='r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        for indice, linha in enumerate(leitor):
            if indice >= limite_linhas:
                break

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


def validar_cenario_normal():
    missao = criar_missao()
    central = CentralDeAlertas()
    motor = MotorDeRegras(missao, central)

    injetar_dados(missao, 5500.0, 3800.0, 2800.0, 88.0, 21.0, 22.0, -48.0, 0.4, 100.0)
    motor.analisar_status_geral()

    severidades = [alerta['severidade'] for alerta in central.fila_de_alertas]
    return severidades == ['NORMAL'] and missao.obter_ultimo_evento() == 'Nenhum evento crítico registrado.'


def validar_cenario_critico():
    missao = criar_missao()
    central = CentralDeAlertas()
    motor = MotorDeRegras(missao, central)

    injetar_dados(missao, 1200.0, 0.0, 3500.0, 18.0, 17.5, 12.0, -60.0, 2.8, 62.0)
    motor.analisar_status_geral()

    severidades = [alerta['severidade'] for alerta in central.fila_de_alertas]
    ultimo_evento = missao.obter_ultimo_evento()
    return 'NORMAL' not in severidades and ('CRITICO' in severidades or 'ALERTA' in severidades) and ultimo_evento.startswith('[CRITICO]')


def validar_previsao():
    missao = criar_missao()
    carregar_amostra_csv(missao, limite_linhas=50)

    analise = AnaliseEnergetica(missao)
    stats = analise.calcular_estatisticas_gerais()
    modelo = ModeloPrevisaoBateria(missao)
    resumo = modelo.exibir_resultado_completo(limite_critico=20.0)

    return bool(stats) and resumo.get('sucesso') and resumo.get('ciclos_analisados') == 51


def executar_validacoes_minimas():
    print("\n=== VALIDACOES MINIMAS DO PROJETO ===\n")

    resultados = [
        ('Cenario normal gera apenas NORMAL', validar_cenario_normal()),
        ('Cenario critico bloqueia NORMAL e registra evento', validar_cenario_critico()),
        ('Previsao executa com amostra real do CSV', validar_previsao()),
    ]

    aprovados = 0
    for titulo, ok in resultados:
        if ok:
            aprovados += 1
            print(f'[PASS] {titulo}')
        else:
            print(f'[FAIL] {titulo}')

    print(f"\nResumo: {aprovados}/{len(resultados)} validacoes aprovadas.")
    print("=== FIM DAS VALIDACOES ===\n")
    return aprovados == len(resultados)


if __name__ == '__main__':
    executar_validacoes_minimas()