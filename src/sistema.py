import csv
from modules.modulos import (
    Missao_espacial, Modulo, 
    SistemaGeracaoSolar, SistemaGeracaoEolica, SistemaArmazenamentoEnergetico,
    SensorDemandaGlobal, SensorTemperaturaInterna, SensorTemperaturaExterna,
    SensorRadicao, SensorO2, SensorIntegridadeEstrutural
)

def main():
    print("=== INICIANDO SISTEMA DE TELEMETRIA DA MISSÃO ===")

    # 1. Início do sistema tipo um BOOT
    missao = Missao_espacial()

    # 2. CRIAÇÃO DOS MÓDULOS PRINCIPAIS <----- Bruno adicionar mais aqui, respeitando a regra da classe
    mod_energia = Modulo('ENE-01', 'Módulo Energético', 'Controle de Energia', 5, consumo=50)
    mod_suporte = Modulo('SUP-01', 'Módulo Suporte à Vida', 'Suporte Vital', 5, consumo=200)
    
    missao.adicionar_modulo(mod_energia)
    missao.adicionar_modulo(mod_suporte)

    # 3. CRIAÇÃO DOS SISTEMAS E SENSORES (Iniciando com valores zerados/padrão) (NÃO MEXER AQUI)
    solar = SistemaGeracaoSolar('Solar-01', capacidade_max_geracao=6000, geracao_atual=0.0)
    eolico = SistemaGeracaoEolica('Eolico-01', capacidade_max_geracao=4000, geracao_atual=0.0)
    bateria = SistemaArmazenamentoEnergetico('Bateria-01', capacidade_max_armazenamento=100)
    
    sensor_demanda = SensorDemandaGlobal('Sensor_Demanda_Total', 'Mede consumo global', 'W', leitura_inicial=0.0)
    sensor_temp_int = SensorTemperaturaInterna('Sensor_Temp_Int', 'Mede Temp Interna', '°C', leitura_inicial=22.0)
    sensor_temp_ext = SensorTemperaturaExterna('Sensor_Temp_Ext', 'Mede Temp Externa', '°C', leitura_inicial=-50.0)
    sensor_radiacao = SensorRadicao('Sensor_Radiacao', 'Mede Nível de Radiação', 'mSv', leitura_inicial=0.0)
    sensor_o2 = SensorO2('Sensor_O2_Principal', 'Mede Nível de Oxigênio', '%', leitura_inicial=21.0)
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

    # 5. INGESTÃO DE DADOS (VEM DO csv
    caminho_csv = 'data/dados.csv'
    print(f"\n[SISTEMA] Iniciando ingestão do arquivo de telemetria '{caminho_csv}'...")
    
    ciclos_lidos = 0

    try:
        with open(caminho_csv, mode='r', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            
            for linha in leitor_csv:
                # Extração e conversão dos dados do cabeçalho unificado (Wide Format)
                ger_solar = float(linha['Geracao_Solar_W'])
                ger_eolico = float(linha['Geracao_Eolica_W'])
                demanda = float(linha['Demanda_Global_W'])
                bat_pct = float(linha['Nivel_Bateria_Pct'])
                o2_pct = float(linha['O2_Pct'])
                temp_int = float(linha['Temp_Int_C'])
                temp_ext = float(linha['Temp_Ext_C'])
                radiacao = float(linha['Radiacao_mSv'])
                integridade = float(linha['Integridade_Pct'])

                # Injetando as leituras nos Sistemas da base
                solar.atualizar_dados(ger_solar, 0.0)
                eolico.atualizar_dados(ger_eolico, 0.0)
                bateria.atualizar_dados(bat_pct, 0.0)

                # Injetando as leituras nos Sensores (usando o método registrar_leitura)
                sensor_demanda.registrar_leitura(demanda)
                sensor_o2.registrar_leitura(o2_pct)
                sensor_temp_int.registrar_leitura(temp_int)
                sensor_temp_ext.registrar_leitura(temp_ext)
                sensor_radiacao.registrar_leitura(radiacao)
                sensor_integridade.registrar_leitura(integridade)
                
                ciclos_lidos += 1
                
                # NOTA PARA A MICHELLY: É exatamente aqui dentro do loop (a cada iteração) 
                # que o Motor de Regras deve ser chamado para rodar as verificações condicionais:
                # motor_de_regras.analisar_status_geral()

        print(f"[SISTEMA] Ingestão concluída. {ciclos_lidos} ciclos temporais armazenados na memória.")

    except FileNotFoundError:
        print(f"Erro Crítico: O arquivo '{caminho_csv}' não foi encontrado na raiz do projeto.")
        return

    # 6. CONSOLIDAÇÃO DA MATRIZ ANALÍTICA (Para o modelo de previsão da Maria)
    print("\n=== MATRIZ DE TELEMETRIA GERADA (Amostra dos últimos 5 ciclos) ===")
    matriz_final = missao.gerar_matriz_telemetria()
    
    if len(matriz_final) > 1:
        # Exibe o cabeçalho estruturado
        print(matriz_final[0])
        # Exibe as últimas 5 linhas preenchidas para validação
        for linha in matriz_final[-5:]:
            print(linha)
    else:
        print("Erro ao gerar matriz analítica: Dados históricos insuficientes.")

if __name__ == "__main__":
    main()