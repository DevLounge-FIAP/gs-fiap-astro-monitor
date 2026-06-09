🚀 Astro Monitor — Sistema de Monitoramento de Missão Espacial
Equipe {Dev}Lounge
IntegranteRMAeltonRM 573694Victor MantovaniRM 570608BrunoRM 572073MichellyRM 573625Maria EduardaRM 572267
Resumo do problema e cenário analisado
O Astro Monitor simula o sistema de controle e monitoramento de uma missão espacial experimental em Marte. A missão opera em ciclos de 5 minutos durante 500 ciclos totais (~41 horas), coletando telemetria de energia, suporte à vida, integridade estrutural e condições ambientais.
O sistema ingere dados de um arquivo CSV (data/dados.csv) gerado com variações realistas, incluindo uma anomalia intencional entre os ciclos 250 e 300: uma tempestade de areia que reduz a geração solar a quase zero, eleva a radiação e degrada levemente a integridade estrutural. Isso testa a capacidade de diagnóstico do motor de regras.
O objetivo é identificar situações críticas automaticamente, gerar alertas priorizados e prever o comportamento da bateria para antecipar decisões operacionais.
Arquivos principais
ArquivoResponsabilidadesrc/sistema.pyOrquestrador principal — menu interativo e fluxo de execuçãosrc/modules/modulos.pyModelos e entidades — Missão, Módulos, Sistemas e Sensoressrc/rules/regras.pyMotor de regras booleanas e diagnósticosrc/rules/alertas.pyCentral de alertas com fila FIFOsrc/forecast/previsao.pyModelo de regressão linear para previsão da bateriasrc/forecast/analise_energetica.pyAnálise descritiva de energia por ciclodata/gerar_dados.pyGerador dos 500 ciclos de telemetria simuladadata/dados.csvArquivo de telemetria utilizado pelo sistema
Estruturas de dados utilizadas e justificativa
EstruturaOnde é usadaPor quêDicionário (dict)self.modulos em Missao_espacial; self.sistemas e self.sensores em ModuloAcesso O(1) por identificador (ex: modulos['ENE-01']), sem necessidade de percorrer listasLista (list)historico_geracao e historico_leituras em Sistema e SensoresArmazena séries temporais; acesso sequencial eficiente para cálculos de média e regressãoFila (deque — FIFO)fila_de_alertas em CentralDeAlertasGarante append e popleft em O(1); alertas processados na ordem de chegadaPilha (list — LIFO)log_eventos_criticos em Missao_espacialRegistra eventos com append e acessa o mais recente por [-1], preservando históricoMatriz (lista de listas)gerar_matriz_telemetria() em Missao_espacialOrganiza leituras por ciclo e variável (Ciclo, Geração, Consumo, Bateria) sem numpyHierarquia de objetosMissao_espacial → Modulo → Sistema / SensorRepresenta a estrutura física da missão: módulos contêm sistemas e sensores acoplados
Observação sobre o fluxo interno: a missão mantém um dicionário de módulos, uma fila de alertas e uma pilha de eventos críticos. A pilha é usada como histórico interno dos eventos críticos gerados pelas regras; a fila garante que os alertas sejam processados na ordem em que foram detectados.
Status dos módulos críticos
Exemplo de tabela de status gerada pelo sistema após análise da telemetria:
MóduloFunçãoStatusENE-01Controle de Energia✅ NormalSUP-01Suporte à Vida✅ NormalCOM-01Comunicação⚠️ AlertaHAB-01Habitat✅ NormalLAB-01Laboratório⚠️ AlertaARM-01Armazenamento✅ Normal
O status de cada módulo é determinado pelo motor de regras com base nas leituras dos sensores acoplados. Módulos com status = False (desligados) ou com sensores fora das faixas de segurança recebem classificação de Alerta ou Crítico.
Regras lógicas principais do diagnóstico
Expressão booleana principal
STATUS_CRITICO = (bateria < 30 AND (solar + eolico) < demanda)
              OR (radiacao > 1 AND solar < 3000)
              OR (o2 < 19 AND temp_int < 15)
              OR (integridade == 0)
              OR (integridade < 70)

Se STATUS_CRITICO = True, o sistema enfileira um alerta CRÍTICO e aciona recomendações automáticas.
Se STATUS_CRITICO = False e todos os parâmetros estão em faixas normais, o sistema confirma status NORMAL.

Tabela de regras implementadas
RegraCondiçãoSeveridadeRecomendaçãoEnergia insuficientebateria < 30 AND (solar + eolico) < demandaCRÍTICODesligar módulos não essenciaisRisco de energiabateria < 50 AND (solar + eolico) < demandaALERTADesligar módulos de baixa criticidadePainéis solares comprometidosradiacao > 1 AND solar < 3000CRÍTICOVerificar estado das placas solaresDiscrepância solarradiacao > 1 AND solar entre 3000 e 4000ALERTAVerificar placas solaresSem geração eólicaNOT eolicoALERTAVerificar integridade das turbinasBateria baixabateria < 50ALERTAEconomizar energiaRisco à vida (combinado)o2 < 19 AND temp_int < 15CRÍTICOVerificar suporte à vida urgenteRisco à vida (isolado)o2 < 19 OR temp_int < 15ALERTAVerificar suporte à vidaIntegridade zeradaNOT integridadeCRÍTICOMódulo destruídoIntegridade críticaintegridade < 70CRÍTICOEnviar reparo imediatoIntegridade degradadaintegridade < 90ALERTAVerificar integridade dos módulosFalha de sensortemp_int > 1000 OR bateria < 0CRÍTICOReiniciar sensores do móduloMódulos estáveisTodos os parâmetros dentro das faixasNORMALSistemas e sensores indicam normalidade
Técnica de previsão utilizada e resultado
Técnica: Regressão linear simples implementada manualmente em src/forecast/previsao.py, sem bibliotecas externas.
Fórmulas utilizadas (least-squares):
m = (n × Σxy − Σx × Σy) / (n × Σx² − (Σx)²)
b = (Σy − m × Σx) / n
Variável analisada: Nível da bateria (%) ao longo dos ciclos de telemetria.
Como influencia o sistema: O modelo é treinado com os 500 ciclos do CSV e projeta o nível da bateria para +10, +50 e +100 ciclos futuros. Se a inclinação m for negativa (bateria em queda), o sistema calcula o ciclo estimado de colapso (limite: 20%) e orienta o operador a acionar medidas preventivas de forma antecipada.
Como executar
Pré-requisito: Python 3 instalado.
bash# Opcional: regenerar os dados simulados
python data/gerar_dados.py

# Executar o sistema principal
python src/sistema.py
O sistema apresenta um menu interativo com as opções:
[1] Simulador de Cenários
[2] Telemetria Completa (CSV)
[3] Análise Energética
[4] Previsão da Bateria
[0] Sair
As rotas de telemetria e análise populam a missão em memória, processam as regras e exibem os resultados no console.
Exemplo de entrada e saída do sistema
Entrada (linha do CSV)
Timestamp,Geracao_Solar_W,Geracao_Eolica_W,Demanda_Global_W,Nivel_Bateria_Pct,O2_Pct,Temp_Int_C,Temp_Ext_C,Radiacao_mSv,Integridade_Pct
2026-01-01 00:00:00,5123.45,1234.56,1789.12,99.75,21.02,22.00,-45.12,0.23,99.98
Saída (cenário de crise energética)
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
Saída da previsão
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
Recomendações geradas pelo sistema
Por ordem de prioridade:

CRÍTICO — Manter suporte à vida e comunicação de emergência
CRÍTICO — Desligar módulos não essenciais (LAB-01, ARM-01)
CRÍTICO — Verificar e reparar integridade estrutural
ALERTA — Verificar estado das placas solares e turbinas eólicas
ALERTA — Economizar energia e desligar módulos de baixa criticidade
ALERTA — Emitir alerta preventivo quando a previsão indicar colapso próximo
NORMAL — Continuar operação padrão quando todos os sistemas estão estáveis

Link do vídeo no YouTube
🎥 Assista à apresentação do Astro Monitor

Conclusões e aprendizados
O Astro Monitor demonstrou como conceitos fundamentais de computação — estruturas de dados, lógica booleana e análise preditiva — podem ser aplicados em um cenário realista e crítico. A equipe saiu do projeto com uma visão mais clara de como sistemas inteligentes tomam decisões baseadas em dados: escolha de estruturas adequadas (dicts e deque) impacta diretamente a performance; implementar regressão linear do zero reforça os fundamentos antes de abstrair para bibliotecas; e simular anomalias reais, como a tempestade de areia nos ciclos 250–300, evidencia como dados inconsistentes testam a robustez de qualquer motor de regras. Essa experiência se conecta diretamente ao que a indústria de tecnologia exige: transformar dados em decisões confiáveis.