import csv
import random
from datetime import datetime, timedelta

# Sistemas (3)
sistemas = [
    {"nome": "Solar Farm 1", "classe": "SistemaGeracaoSolar"},
    {"nome": "Turbina Eolica 1", "classe": "SistemaGeracaoEolica"},
    {"nome": "Banco Baterias 1", "classe": "SistemaArmazenamentoEnergetico"},
]

# Sensores (10)
sensores = [
    {"nome": "Irradiacao_Sensor", "tipo": "Sensor de Irradiação Solar", "classe": "SensorIrradiacao", "unidade": "W/m²", "faixa": (0, 1200)},
    {"nome": "VelocidadeVento_Sensor", "tipo": "Sensor de Velocidade do Vento", "classe": "SensorVelocidadeVento", "unidade": "m/s", "faixa": (0, 30)},
    {"nome": "NivelEnergia_Sensor", "tipo": "Sensor da Bateria", "classe": "SensorNivelEnergia", "unidade": "%", "faixa": (0, 100)},
    {"nome": "O2_Sensor", "tipo": "Sensor do Oxigênio", "classe": "SensorO2", "unidade": "%", "faixa": (15, 25)},
    {"nome": "TemperaturaInterna_Sensor", "tipo": "Sensor da Temperatura Interna", "classe": "SensorTemperaturaInterna", "unidade": "°C", "faixa": (18, 28)},
    {"nome": "QualidadeSinal_Sensor", "tipo": "Sensor da Qualidade do Sinal", "classe": "SensorQualidadeSinal", "unidade": "%", "faixa": (0, 100)},
    {"nome": "IntegridadeEstrutural_Sensor", "tipo": "Sensor da Integridade Estrutural", "classe": "SensorIntegridadeEstrutural", "unidade": "%", "faixa": (80, 100)},
    {"nome": "TemperaturaExterna_Sensor", "tipo": "Sensor da Temperatura Externa", "classe": "SensorTemperaturaExterna", "unidade": "°C", "faixa": (-50, 50)},
    {"nome": "Radiacao_Sensor", "tipo": "Sensor da Radiação", "classe": "SensorRadicao", "unidade": "mSv/h", "faixa": (0, 500)},
    {"nome": "Helio3_Sensor", "tipo": "Sensor do Hélio 3", "classe": "SensorHelio3", "unidade": "ppm", "faixa": (0, 1000)},
]

linhas_por_combinacao = 500
dados = []
timestamp_base = datetime(2025, 1, 1, 0, 0, 0)

print("Gerando CSV com 10 sensores × 3 sistemas × 500 linhas...")

for sistema in sistemas:
    for sensor in sensores:
        print(f"Processando: {sensor['nome']} → {sistema['nome']}")
        ultimo_valor = None
        for i in range(linhas_por_combinacao):
            # Irradiação solar
            if sensor["tipo"] == "Sensor de Irradiação Solar":
                hora = (timestamp_base + timedelta(minutes=i*5)).hour
                fator = max(0, 1 - abs(hora - 12) / 12)
                valor = random.uniform(0, sensor["faixa"][1] * fator)
            # Bateria
            elif sensor["tipo"] == "Sensor da Bateria":
                if ultimo_valor is None:
                    valor = random.uniform(40, 90)
                else:
                    delta = random.uniform(-5, 5)
                    valor = max(0, min(100, ultimo_valor + delta))
            # Demais sensores
            else:
                if ultimo_valor is None:
                    valor = random.uniform(sensor["faixa"][0], sensor["faixa"][1])
                else:
                    variacao = random.uniform(-sensor["faixa"][1]*0.02, sensor["faixa"][1]*0.02)
                    valor = max(sensor["faixa"][0], min(sensor["faixa"][1], ultimo_valor + variacao))
            ultimo_valor = valor

            dados.append({
                "timestamp": (timestamp_base + timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S"),
                "sensor_nome": sensor["nome"],
                "sensor_tipo": sensor["tipo"],
                "sensor_classe": sensor["classe"],
                "sistema_nome": sistema["nome"],
                "sistema_classe": sistema["classe"],
                "valor_leitura": round(valor, 2),
                "unidade": sensor["unidade"]
            })

# Salvar CSV
arquivo = "dados.csv"
with open(arquivo, 'w', newline='', encoding='utf-8') as f:
    campos = ["timestamp", "sensor_nome", "sensor_tipo", "sensor_classe",
              "sistema_nome", "sistema_classe", "valor_leitura", "unidade"]
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()
    writer.writerows(dados)

print(f"\n✅ Arquivo '{arquivo}' gerado com sucesso!")
print(f"📊 Total de linhas: {len(dados)}")
print(f"🔢 Combinações: {len(sistemas)} sistemas × {len(sensores)} sensores = {len(sistemas)*len(sensores)}")
print(f"🎯 Linhas por combinação: {linhas_por_combinacao}")