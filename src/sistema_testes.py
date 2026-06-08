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

# ============================================================
#  1. CRIAÇÃO DA INFRAESTRUTURA
# ============================================================
def criar_missao():
    missao = Missao_espacial()

    # CRIAÇÃO DOS 6 MÓDULOS OBRIGATÓRIOS (Regra 7.1 da Rubrica)
    mod_energia       = Modulo('ENE-01', 'Módulo Energético', 'Controle de Energia', 5, consumo=50)
    mod_suporte       = Modulo('SUP-01', 'Módulo Suporte à Vida', 'Suporte Vital', 5, consumo=200)
    mod_comunicacao   = Modulo('COM-01', 'Módulo Comunicação', 'Transmissão', 4, consumo=100)
    mod_habitat       = Modulo('HAB-01', 'Módulo Habitat', 'Alojamento', 3, consumo=150)
    mod_laboratorio   = Modulo('LAB-01', 'Módulo Laboratório', 'Pesquisa', 3, consumo=300)
    mod_armazenamento = Modulo('ARM-01', 'Módulo Armazenamento', 'Estoque', 2, consumo=50)
    
    missao.adicionar_modulo(mod_energia)
    missao.adicionar_modulo(mod_suporte)
    missao.adicionar_modulo(mod_comunicacao)
    missao.adicionar_modulo(mod_habitat)
    missao.adicionar_modulo(mod_laboratorio)
    missao.adicionar_modulo(mod_armazenamento)

    # CRIAÇÃO DOS SISTEMAS E SENSORES
    solar   = SistemaGeracaoSolar('Solar-01', capacidade_max_geracao=6000, geracao_atual=0.0)
    eolico  = SistemaGeracaoEolica('Eolico-01', capacidade_max_geracao=4000, geracao_atual=0.0)
    bateria = SistemaArmazenamentoEnergetico('Bateria-01', capacidade_max_armazenamento=100)
    
    sensor_demanda     = SensorDemandaGlobal('Sensor_Demanda_Total', 'Mede consumo global', 'W', leitura_inicial=0.0)
    sensor_temp_int    = SensorTemperaturaInterna('Sensor_Temp_Int', 'Mede Temp Interna', '°C', leitura_inicial=22.0)
    sensor_temp_ext    = SensorTemperaturaExterna('Sensor_Temp_Ext', 'Mede Temp Externa', '°C', leitura_inicial=-50.0)
    sensor_radiacao    = SensorRadicao('Sensor_Radiacao', 'Mede Nível de Radiação', 'mSv', leitura_inicial=0.0)
    sensor_o2          = SensorO2('Sensor_O2_Principal', 'Mede Nível de Oxigênio', '%', leitura_inicial=21.0)
    sensor_integridade = SensorIntegridadeEstrutural('Sensor_Integridade', 'Mede Saúde do Casco', '%', leitura_inicial=100.0)

    # ACOPLAMENTO DOS SENSORES AOS MÓDULOS
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

# ============================================================
#  2. FUNÇÃO FERRAMENTA: INJEÇÃO DE DADOS
# ============================================================
def injetar_dados(missao, solar_w, eolico_w, demanda_w, bateria_pct, o2_pct, temp_int, temp_ext, radiacao, integridade):
    '''Atualiza o estado interno da missão buscando os objetos em O(1) pelo Dicionário.'''
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

# ============================================================
#  3. FUNÇÕES DO MENU INTERATIVO
# ============================================================
def mostrar_alertas(central):
    quantidade = central.obter_quantidade_alertas_pendentes()
    if quantidade == 0:
        print("  ✅ Nenhum alerta gerado. Status Nominal.")
        return
    print(f"\n  ⚠️ {quantidade} alerta(s) encontrado(s):\n")
    while central.obter_quantidade_alertas_pendentes() > 0:
        alerta = central.processar_proximo_alerta()
        print(f"  [{alerta['severidade']}] {alerta['mensagem']}")
        print(f"  Recomendação: {alerta['recomendacao']}\n")

def simulador_de_cenarios():
    print("\n  Escolha um cenário:")
    print("  [1] Operação Normal")
    print("  [2] Crise Energética")
    print("  [3] Tempestade de Radiação")
    print("  [0] Voltar\n")

    opcao = input("  Opção: ").strip()
    if opcao == '0': return

    missao = criar_missao()
    central = CentralDeAlertas()
    motor = MotorDeRegras(missao, central)

    # Injeção de cenário isolado
    if opcao == '1':
        injetar_dados(missao, 5500.0, 3800.0, 2800.0, 88.0, 21.0, 22.0, -48.0, 0.4, 100.0)
    elif opcao == '2':
        injetar_dados(missao, 200.0, 0.0, 3500.0, 18.0, 21.0, 21.5, -55.0, 0.3, 100.0)
    elif opcao == '3':
        injetar_dados(missao, 1200.0, 3500.0, 3000.0, 55.0, 20.8, 21.0, -40.0, 2.8, 68.0)
    else:
        print("  Opção Inválida.")
        return

    motor.analisar_status_geral()
    print("\n  --- Alertas gerados no Cenário ---")
    mostrar_alertas(central)

def telemetria_csv():
    caminho_csv = 'data/dados.csv'
    print(f"\n[SISTEMA] Iniciando ingestão do arquivo de telemetria '{caminho_csv}'...")
    
    missao = criar_missao()
    central = CentralDeAlertas()
    motor = MotorDeRegras(missao, central)
    ciclos_lidos = 0

    try:
        with open(caminho_csv, mode='r', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for linha in leitor_csv:
                # O laço FOR usando a função "ferramenta" (Muito mais limpo)
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
                ciclos_lidos += 1

        print(f"[SISTEMA] Ingestão concluída. {ciclos_lidos} ciclos armazenados na memória.")
        
        # Gerar e exibir a matriz após carregar os dados
        print("\n=== MATRIZ DE TELEMETRIA GERADA (Amostra dos últimos 2 ciclos) ===")
        matriz_final = missao.gerar_matriz_telemetria()
        if len(matriz_final) > 1:
            print(matriz_final[0])
            for l in matriz_final[-2:]: print(l)

    except FileNotFoundError:
        print(f"Erro Crítico: O arquivo '{caminho_csv}' não foi encontrado.")

# ============================================================
#  4. LOOP DO MENU PRINCIPAL
# ============================================================
def main():
    print("=" * 50)
    print("   ASTRO MONITOR - CENTRO DE CONTROLE DA MISSÃO")
    print("=" * 50)

    while True:
        print("\n  [1] Simulador de Cenários Rápidos")
        print("  [2] Rodar Telemetria Completa (CSV)")
        print("  [0] Sair\n")

        opcao = input("  Escolha uma opção de comando: ").strip()

        if opcao == '1':
            simulador_de_cenarios()
        elif opcao == '2':
            telemetria_csv()
        elif opcao == '0':
            print("\nEncerrando sistema. Desconexão segura.")
            break
        else:
            print("❌ Comando inválido.")

if __name__ == "__main__":
    main()