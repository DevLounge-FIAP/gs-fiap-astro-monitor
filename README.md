# 🚀 Astro Monitor — Sistema de Monitoramento de Missão Espacial

## Equipe {Dev}Lounge

| Integrante | RM |
|---|---|
| Aelton | RM 573694 |
| Victor Mantovani | RM 570608 |
| Bruno | RM 572073 |
| Michelly | RM 573625 |
| Maria Eduarda | RM 572267 |


## Resumo do problema e cenário analisado

O **Astro Monitor** simula o sistema de controle e monitoramento de uma missão espacial experimental em Marte. A missão opera em ciclos de 5 minutos durante 500 ciclos totais (~41 horas), coletando telemetria de energia, suporte à vida, integridade estrutural e condições ambientais.

O sistema ingere dados de um arquivo CSV (`data/dados.csv`) gerado com variações realistas, incluindo uma **anomalia intencional** entre os ciclos 250 e 300: uma tempestade de areia que reduz a geração solar a quase zero, eleva a radiação e degrada levemente a integridade estrutural. Isso testa a capacidade de diagnóstico do motor de regras.

O objetivo é identificar situações críticas automaticamente, gerar alertas priorizados e prever o comportamento da bateria para antecipar decisões operacionais.


## Arquivos principais

| Arquivo | Responsabilidade |
|---|---|
| `src/sistema.py` | Orquestrador principal — menu interativo e fluxo de execução |
| `src/modules/modulos.py` | Modelos e entidades — Missão, Módulos, Sistemas e Sensores |
| `src/rules/regras.py` | Motor de regras booleanas e diagnóstico |
| `src/rules/alertas.py` | Central de alertas com fila FIFO |
| `src/forecast/previsao.py` | Modelo de regressão linear para previsão da bateria |
| `src/forecast/analise_energetica.py` | Análise descritiva de energia por ciclo |
| `data/gerar_dados.py` | Gerador dos 500 ciclos de telemetria simulada |
| `data/dados.csv` | Arquivo de telemetria utilizado pelo sistema |


## Estruturas de dados utilizadas e justificativa

| Estrutura | Onde é usada | Por quê |
|---|---|---|
| **Dicionário (`dict`)** | `self.modulos` em `Missao_espacial`; `self.sistemas` e `self.sensores` em `Modulo` | Acesso O(1) por identificador (ex: `modulos['ENE-01']`), sem necessidade de percorrer listas |
| **Lista (`list`)** | `historico_geracao` e `historico_leituras` em `Sistema` e `Sensores` | Armazena séries temporais; acesso sequencial eficiente para cálculos de média e regressão |
| **Fila (`deque` — FIFO)** | `fila_de_alertas` em `CentralDeAlertas` | Garante `append` e `popleft` em O(1); alertas processados na ordem de chegada |
| **Pilha (`list` — LIFO)** | `log_eventos_criticos` em `Missao_espacial` | Registra eventos com `append` e acessa o mais recente por `[-1]`, preservando histórico |
| **Matriz (lista de listas)** | `gerar_matriz_telemetria()` em `Missao_espacial` | Organiza leituras por ciclo e variável (Ciclo, Geração, Consumo, Bateria) sem numpy |
| **Hierarquia de objetos** | `Missao_espacial → Modulo → Sistema / Sensor` | Representa a estrutura física da missão: módulos contêm sistemas e sensores acoplados |

**Observação sobre o fluxo interno:** a missão mantém um dicionário de módulos, uma fila de alertas e uma pilha de eventos críticos. A pilha é usada como histórico interno dos eventos críticos gerados pelas regras; a fila garante que os alertas sejam processados na ordem em que foram detectados.

## Status dos módulos críticos

Exemplo de tabela de status gerada pelo sistema após análise da telemetria:

| Módulo | Função | Status |
|---|---|---|
| ENE-01 | Controle de Energia | ✅ Normal |
| SUP-01 | Suporte à Vida | ✅ Normal |
| COM-01 | Comunicação | ⚠️ Alerta |
| HAB-01 | Habitat | ✅ Normal |
| LAB-01 | Laboratório | ⚠️ Alerta |
| ARM-01 | Armazenamento | ✅ Normal |

O status de cada módulo é determinado pelo motor de regras com base nas leituras dos sensores acoplados. Módulos com `status = False` (desligados) ou com sensores fora das faixas de segurança recebem classificação de Alerta ou Crítico.


## Regras lógicas principais do diagnóstico

### Expressão booleana principal

```
STATUS_CRITICO = (bateria < 30 AND (solar + eolico) < demanda)
              OR (radiacao > 1 AND solar < 3000)
              OR (o2 < 19 AND temp_int < 15)
              OR (integridade == 0)
              OR (integridade < 70)
```

> Se `STATUS_CRITICO = True`, o sistema enfileira um alerta CRÍTICO e aciona recomendações automáticas.  
> Se `STATUS_CRITICO = False` e todos os parâmetros estão em faixas normais, o sistema confirma status NORMAL.

### Tabela de regras implementadas

| Regra | Condição | Severidade | Recomendação |
|---|---|---|---|
| Energia insuficiente | `bateria < 30 AND (solar + eolico) < demanda` | CRÍTICO | Desligar módulos não essenciais |
| Risco de energia | `bateria < 50 AND (solar + eolico) < demanda` | ALERTA | Desligar módulos de baixa criticidade |
| Painéis solares comprometidos | `radiacao > 1 AND solar < 3000` | CRÍTICO | Verificar estado das placas solares |
| Discrepância solar | `radiacao > 1 AND solar entre 3000 e 4000` | ALERTA | Verificar placas solares |
| Sem geração eólica | `NOT eolico` | ALERTA | Verificar integridade das turbinas |
| Bateria baixa | `bateria < 50` | ALERTA | Economizar energia |
| Risco à vida (combinado) | `o2 < 19 AND temp_int < 15` | CRÍTICO | Verificar suporte à vida urgente |
| Risco à vida (isolado) | `o2 < 19 OR temp_int < 15` | ALERTA | Verificar suporte à vida |
| Integridade zerada | `NOT integridade` | CRÍTICO | Módulo destruído |
| Integridade crítica | `integridade < 70` | CRÍTICO | Enviar reparo imediato |
| Integridade degradada | `integridade < 90` | ALERTA | Verificar integridade dos módulos |
| Falha de sensor | `temp_int > 1000 OR bateria < 0` | CRÍTICO | Reiniciar sensores do módulo |
| Módulos estáveis | Todos os parâmetros dentro das faixas | NORMAL | Sistemas e sensores indicam normalidade |


## Técnica de previsão utilizada e resultado

**Técnica:** Regressão linear simples implementada manualmente em `src/forecast/previsao.py`, sem bibliotecas externas.

**Fórmulas utilizadas (least-squares):**

```
m = (n × Σxy − Σx × Σy) / (n × Σx² − (Σx)²)
b = (Σy − m × Σx) / n
```

**Variável analisada:** Nível da bateria (%) ao longo dos ciclos de telemetria.

**Como influencia o sistema:** O modelo é treinado com os 500 ciclos do CSV e projeta o nível da bateria para +10, +50 e +100 ciclos futuros. Se a inclinação `m` for negativa (bateria em queda), o sistema calcula o ciclo estimado de colapso (limite: 20%) e orienta o operador a acionar medidas preventivas de forma antecipada.


## Como executar

**Pré-requisito:** Python 3 instalado.

```bash
# Opcional: regenerar os dados simulados
python data/gerar_dados.py

# Executar o sistema principal
python src/sistema.py
```

O sistema apresenta um menu interativo com as opções:

```
[1] Simulador de Cenários
[2] Telemetria Completa (CSV)
[3] Análise Energética
[4] Previsão da Bateria
[5] Validações Mínimas
[0] Sair
```

As rotas de telemetria e análise populam a missão em memória, processam as regras e exibem os resultados no console.


## Exemplo de entrada e saída do sistema

### Entrada (linha do CSV)

```
Timestamp,Geracao_Solar_W,Geracao_Eolica_W,Demanda_Global_W,Nivel_Bateria_Pct,O2_Pct,Temp_Int_C,Temp_Ext_C,Radiacao_mSv,Integridade_Pct
2026-01-01 00:00:00,5123.45,1234.56,1789.12,99.75,21.02,22.00,-45.12,0.23,99.98
```

### Saída (cenário de crise energética)

```
=== Simulando: Crise Energetica ===

  Solar          : 200.0 W
  Eólico         : 0.0 W
  Bateria        : 18.0 %
  Demanda        : 3500.0 W

  --- Alertas gerados ---

  [CRÍTICO] Energia insuficiente
  Recomendação: Desligar módulos não essenciais

  [ALERTA] Sem produção de energia eólica
  Recomendação: Verifique integridade das turbinas eólicas

  [ALERTA] Bateria com baixo nível de energia
  Recomendação: Considere economizar energia
```

### Saída da previsão

```
[PREVISAO] Modelo treinado com 500 ciclos de telemetria.
[PREVISAO] Inclinacao (m): -0.01234 | Interceptacao (b): 85.24

 TENDENCIA: QUEDA (-0.01234% por ciclo)

 --- Projecao para proximos ciclos ---
   Ciclo  510: 70.2%
   Ciclo  550: 64.1%
   Ciclo  600: 57.8%

 --- Previsao de colapso (limite: 20%) ---
   Ciclo de risco   : 1200
   Ciclos restantes : 700
```


## Recomendações geradas pelo sistema

Por ordem de prioridade:

1. **CRÍTICO** — Manter suporte à vida e comunicação de emergência
2. **CRÍTICO** — Desligar módulos não essenciais (LAB-01, ARM-01)
3. **CRÍTICO** — Verificar e reparar integridade estrutural
4. **ALERTA** — Verificar estado das placas solares e turbinas eólicas
5. **ALERTA** — Economizar energia e desligar módulos de baixa criticidade
6. **ALERTA** — Emitir alerta preventivo quando a previsão indicar colapso próximo
7. **NORMAL** — Continuar operação padrão quando todos os sistemas estão estáveis


## Link do vídeo no YouTube

🎥 [Assista à apresentação do Astro Monitor](https://www.youtube.com/watch?v=NpEUCEKVi34)


## Conclusões e aprendizados

O Astro Monitor demonstrou como conceitos fundamentais de computação — estruturas de dados, lógica booleana e análise preditiva — podem ser aplicados em um cenário realista e crítico. A equipe saiu do projeto com uma visão mais clara de como sistemas inteligentes tomam decisões baseadas em dados: escolha de estruturas adequadas (dicts e deque) impacta diretamente a performance; implementar regressão linear do zero reforça os fundamentos antes de abstrair para bibliotecas; e simular anomalias reais, como a tempestade de areia nos ciclos 250–300, evidencia como dados inconsistentes testam a robustez de qualquer motor de regras. Essa experiência se conecta diretamente ao que a indústria de tecnologia exige: transformar dados em decisões confiáveis.