import csv
import random
import math
from datetime import datetime, timedelta

def gerar_dados_simulados():
    dados = []
    timestamp_base = datetime(2026, 1, 1, 0, 0)
    
    # Variáveis de Estado Inicial (vão sofrendo alterações ao longo do tempo)
    nivel_bateria = 100.0
    integridade_estrutural = 100.0
    o2_atual = 21.0
    temp_int_atual = 22.0
    
    total_ciclos = 500

    print("Iniciando geração de dados (Wide Format)...")

    for i in range(total_ciclos):
        timestamp_atual = (timestamp_base + timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S")
        
        # LÓGICA DE EVENTOS DA MISSÃO
        # Simulando uma anomalia (Tempestade de Areia) entre o ciclo 250 e 300
        em_tempestade = 250 <= i <= 300
        # Regra da tempestade
        # --- SIMULAÇÃO DE ENERGIA ---
        if em_tempestade:
            geracao_solar = random.uniform(0, 50) # Painéis cobertos de poeira
            geracao_eolica = random.uniform(2500, 3500) # Ventos fortes
            demanda_global = random.uniform(2500, 3200) # Base gasta mais energia para aquecimento
        else:
            # Ciclo diurno normal usando Seno (Sobe de dia, zera de noite)
            hora_dia = (i * 5) % 1440 # Minutos em um dia
            fator_sol = max(0, math.sin(math.pi * hora_dia / 720)) 
            geracao_solar = fator_sol * random.uniform(4800, 5200)
            
            geracao_eolica = random.uniform(500, 2000) # Vento normal
            demanda_global = random.uniform(1500, 2200) # Consumo normal

        #SIMULAÇÃO DA BATERIA
        # Se gera mais que consome, carrega. Se consome mais, descarrega.
        saldo_energia = (geracao_solar + geracao_eolica) - demanda_global
        
        # Considerando que 1% de bateria equivale a 100W de saldo num ciclo de 5 min (valor arbitrário para simulação)
        impacto_bateria = saldo_energia / 100.0 
        nivel_bateria += impacto_bateria
        
        # Travas de segurança da física (Bateria não passa de 100 nem cai abaixo de 0)
        # Aqui é preciosismo da minha parte (Aelton)
        nivel_bateria = max(0.0, min(100.0, nivel_bateria))

        # SIMULAÇÃO DOS SENSORES DE SUPORTE À VIDA E ESTRUTURA
        if em_tempestade:
            temp_ext = random.uniform(-100, -80)
            radiacao = random.uniform(2.0, 5.0) # Radiação sobe
            integridade_estrutural -= random.uniform(0.01, 0.05) # Estrutura sofre dano leve
            temp_int_atual -= random.uniform(0.01, 0.1) # Temperatura interna começa a cair levemente
        else:
            temp_ext = random.uniform(-60, -30)
            radiacao = random.uniform(0.1, 0.5)
            # Sistema tenta estabilizar a temperatura interna em 22.0
            temp_int_atual += (22.0 - temp_int_atual) * 0.1 + random.uniform(-0.1, 0.1)

        # O2 varia levemente com o tempo (aplicando um random com path)
        o2_atual += random.uniform(-0.05, 0.05)
        o2_atual = max(18.0, min(23.0, o2_atual))

        linha = {
            "Timestamp": timestamp_atual,
            "Geracao_Solar_W": round(geracao_solar, 2),
            "Geracao_Eolica_W": round(geracao_eolica, 2),
            "Demanda_Global_W": round(demanda_global, 2),
            "Nivel_Bateria_Pct": round(nivel_bateria, 2),
            "O2_Pct": round(o2_atual, 2),
            "Temp_Int_C": round(temp_int_atual, 2),
            "Temp_Ext_C": round(temp_ext, 2),
            "Radiacao_mSv": round(radiacao, 2),
            "Integridade_Pct": round(integridade_estrutural, 2)
        }
        
        dados.append(linha)

    # SALVANDO O ARQUIVO CSV
    arquivo = "data/dados.csv"
    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        # As chaves do dicionário formam o cabeçalho perfeito
        campos = dados[0].keys()
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

    print(f"✅ Arquivo '{arquivo}' gerado com sucesso no formato consolidado!")
    print(f"Foram gerados {total_ciclos} ciclos temporais sincronizados.")

if __name__ == "__main__":
    gerar_dados_simulados()