# gs-fiap-astro-monitor

**Equipe**
- **Nome da equipe**: {Dev}Lounge
- **Integrantes (RM)**: Aelton - RM 573694; Victor - RM 570608; Bruno - RM 572073; Michelly - RM 573625; Maria - RM 572267

**Resumo do problema e cenário analisado**
- **Resumo**: Projeto de monitoramento e diagnóstico de telemetria para uma missão espacial fictícia. O sistema ingere dados de telemetria (geração solar/eólica, consumo, nível de bateria, O2, temperatura, radiação, integridade estrutural) e executa análises descritivas, diagnóstico por regras e previsões simples sobre o nível da bateria.
- **Cenário**: Simulação de 500 ciclos temporais (arquivo [data/dados.csv](data/dados.csv#L1-L20) gerado por [data/gerar_dados.py](data/gerar_dados.py#L1-L200)) incluindo eventos anômalos (ex.: tempestade de areia) que afetam geração, demanda e integridade.

**Arquivos principais**
- **Orquestrador**: [src/sistema.py](src/sistema.py#L1-L400)
- **Modelos / Entidades**: [src/modules/modulos.py](src/modules/modulos.py#L1-L400)
- **Regras e alertas**: [src/rules/regras.py](src/rules/regras.py#L1-L300) e [src/rules/alertas.py](src/rules/alertas.py#L1-L200)
- **Análise e previsão**: [src/forecast/analise_energetica.py](src/forecast/analise_energetica.py#L1-L400) e [src/forecast/previsao.py](src/forecast/previsao.py#L1-L400)

**Estruturas de dados: quais foram usadas e por quê**
- **Dicionários (`dict`)**: usados para armazenar módulos por chave (`self.modulos`) oferecendo acesso O(1) por identificador - ideal para localizar módulos rapidamente.
- **Listas (`list`)**: usadas como matrizes de telemetria (lista de listas) e para histórico de leituras em sensores/sistemas por simplicidade e iteração sequencial.
- **Deque (`collections.deque`)**: usado em `CentralDeAlertas` para implementar fila FIFO eficiente (append/popleft em O(1)).
- **Pilha (lista como LIFO)**: `log_eventos_criticos` atua como pilha para eventos críticos, preservando histórico de ocorrências.

**Regras lógicas principais do diagnóstico**
- Regra Energia: se `bateria < 30%` e `(solar + eolico) < demanda` → alerta CRÍTICO sugerindo desligar módulos não essenciais.
- Risco de energia: se `bateria < 50%` e geração insuficiente → alerta ALERTA recomendando economia/desligamento de módulos de baixa criticidade.
- Produção solar vs radiação: discordância entre radiação elevada e baixa geração → alerta (CRÍTICO/ALERTA) para checagem das placas.
- Produção eólica: ausência de geração eólica → alerta para integridade das turbinas.
- Bateria baixa/zerada: alertas específicos em `bateria < 50%` e `bateria == 0`.
- Suporte à vida: `O2 < 19%` e `Temp_Int < 15°C` combinados → CRÍTICO (risco à vida); condições isoladas → ALERTA.
- Integridade estrutural: `integridade == 0` → CRÍTICO; `integridade < 70` → CRÍTICO (reparo); `integridade < 90` → ALERTA.
- Estado estável: se bateria alta e geração maior que demanda e O2/Temp dentro de faixas seguras → alerta NORMAL.

**Técnica de previsão utilizada e resultado**
- Técnica: regressão linear simples implementada manualmente em `ModeloPrevisaoBateria` ([src/forecast/previsao.py](src/forecast/previsao.py#L1-L300)). O modelo calcula coeficientes `m` e `b` usando somas (fórmulas clássicas de least-squares sem bibliotecas).
- Objetivo: prever o nível da bateria por ciclo e estimar o ciclo em que a bateria atingirá um limite crítico (ex.: 20%).
- Resultado esperado: ao treinar o modelo com a matriz gerada, o sistema imprime a inclinação (`m`) e a interceptação (`b`), projeta níveis para +10/+50/+100 ciclos e indica o ciclo de risco (ou informa que não há tendência de queda).

**Como executar**
- Pré-requisito: ter Python 3 instalado e o ambiente virtual opcionalmente ativado.
- Gerar dados de teste (opcional):

```bash
python data/gerar_dados.py
```

- Executar o orquestrador principal:

```bash
python src/sistema.py
```

O comando acima inicia a ingestão do arquivo `data/dados.csv`, popula estruturas em memória, e exibe uma amostra da matriz gerada.

**Exemplo de entrada e saída do sistema**
- Exemplo de linha (entrada) no CSV (`data/dados.csv`):

- Timestamp,Geracao_Solar_W,Geracao_Eolica_W,Demanda_Global_W,Nivel_Bateria_Pct,O2_Pct,Temp_Int_C,Temp_Ext_C,Radiacao_mSv,Integridade_Pct
- 2026-01-01 00:00:00,5123.45,1234.56,1789.12,99.75,21.02,22.00,-45.12,0.23,99.98

- Exemplo (trecho) de saída esperada no console:

- [SISTEMA] Iniciando ingestão do arquivo de telemetria 'data/dados.csv'...
- [SISTEMA] Ingestão concluída. 500 ciclos temporais armazenados na memória.
- === MATRIZ DE TELEMETRIA GERADA (Amostra dos últimos 5 ciclos) ===
- ['Ciclo', 'Geração_Total_W', 'Consumo_Total_W', 'Nível_Bateria_%']
- [495, 6234.21, 2100.34, 72.45]
- [496, 5123.12, 2050.55, 71.87]
- ...
- [PREVISAO] Modelo treinado com 500 ciclos de telemetria.
- [PREVISAO] Inclinacao (m): -0.01234 | Interceptacao (b): 85.24
-    Ciclo 510: 70.2%
-    Ciclo 550: 64.1%
- Previsão de colapso: Ciclo de risco : 1200 (exemplo)

**Recomendações geradas pelo sistema**
- Desligar módulos não essenciais (quando energia crítica).
- Desligar módulos de baixa criticidade / economia de energia (risco energético).
- Verificar/inspecionar placas solares (discrepância radiação x geração).
- Verificar turbinas eólicas (sem produção).
- Checar/reparar integridade estrutural (níveis críticos).
- Verificar módulo de suporte à vida imediatamente (O2/temperatura críticas).

**Link do vídeo no YouTube**
- Demonstração / apresentação (substitua pelo link final): Colocar o link do vídeo aqui depois.

**Conclusões e aprendizados**
- O projeto integra três frentes educacionais importantes: engenharia de software orientada a objetos, lógica de sistemas (motor de regras) e técnicas básicas de análise preditiva.
- Aprendizados técnicos: escolha de estruturas de dados adequadas (dicts e deque) melhora performance/clareza; implementar regressão manual ajuda a entender os fundamentos antes de usar bibliotecas.
- Pontos de melhoria futuros: adicionar testes automatizados, modularizar o motor de regras para permitir políticas configuráveis, usar bibliotecas de ML (scikit-learn) para modelos mais robustos e adicionar persistência/visualização dos resultados.

---
Para detalhes de implementação, veja os arquivos fonte listados acima.
