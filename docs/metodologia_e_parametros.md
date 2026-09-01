# Documentação Metodológica e Arquitetural Detalhada

> **TCC — MBA em Data Science e Analytics**  
> **Tema:** Predição de Letalidade Hospitalar por IAM no SUS utilizando Machine Learning e Análise de Sobrevivência  
> **Última Atualização:** Setembro de 2026

Este documento visa detalhar meticulosamente todas as decisões metodológicas, estatísticas e computacionais tomadas durante a construção do pipeline de dados. O objetivo é fornecer transparência e reprodutibilidade acadêmica rigorosa para cada parâmetro escolhido, garantindo que a banca avaliadora compreenda exatamente a lógica por trás da engenharia de dados e modelagem matemática.

---

## 1. Estratégia de Coleta e Conversão de Dados Brutos (Notebooks 01a e 01b)

### 1.1 Delimitação Temporal e Geográfica
- **Coorte:** Estado de São Paulo (SP).
- **Período Histórico:** 2015 a 2025 (11 anos ininterruptos).
- **Justificativa Científica:** A expansão do escopo para 11 anos não apenas eleva a volumetria de dados para **415.367 internações**, como permite que o modelo aprenda padrões macroeconômicos e epidemiológicos ao longo de uma década inteira, mitigando vieses de curto prazo (como flutuações sazonais ou pandêmicas atípicas).

### 1.2 O Ecossistema de Conversão (Arquivos .DBC)
Os dados brutos do DATASUS são fornecidos no formato proprietário hiper-comprimido `.dbc`. 
- **Engenharia:** Utilizamos a biblioteca `datasus-dbc` para descomprimir o formato para um `.dbf` intermediário e o `dbfread` para conversão final em CSV (`utf-8`).
- **Justificativa:** Diferente das consultas manuais no site do TabNet (agregadas), os arquivos nativos `.dbc` via FTP fornecem granularidade de **nível de paciente** (linha a linha), exigência inegociável para modelagem preditiva *patient-level*.

### 1.3 Mapeamento Categórico via TabWin (Arquivos .CNV)
- **Problema Intrínseco:** Variáveis categóricas do SUS (ex: Raça, Tipo de Leito) vêm em códigos arbitrários (ex: `1`, `2`).
- **Solução Implementada:** Construímos um motor de tradução que absorve os dicionários de formatação originais do Ministério da Saúde (`.def` e `.cnv`).
- **Tratamento de Padding:** Para resolver falhas históricas de *join* (onde o código original "1" não batia com o dicionário "01"), implementamos um duplo mapeamento algorítmico, injetando no dicionário python as versões puras e com *zero-padding*. O multiprocessamento foi utilizado para paralelizar a tradução dos mais de 720 arquivos.

---

## 2. ETL e Engenharia de Dados (Notebook 02)

### 2.1 Seleção da Coorte Clínica
- **CID-10 Principal e Secundário:** Filtro por Infarto Agudo do Miocárdio (`I21`, compreendendo `I21.0` a `I21.9`).
- **Filtro Etário:** Adultos ≥ 18 anos.
- **Justificativa:** O IAM pediátrico (ou congênito mascarado) apresenta mecanismos fisiopatológicos e trajetórias de sobrevida fundamentalmente distintos do IAM aterosclerótico adulto. Excluir dados de menores de 18 anos suprime ruídos e garante homogeneidade estatística da população modelada.

### 2.2 Threshold de Dados Ausentes
- **Regra de Exclusão:** Colunas com > 70% de nulos foram deletadas.
- **Justificativa:** Variáveis com densidade informacional inferior a 30% em bases governamentais não podem ser imputadas de maneira segura, pois a imputação (seja por mediana ou regressão) inventaria a maior parte da informação, destruindo a validade científica do modelo.

### 2.3 Arquitetura de Merge Longitudinal (SIH x CNES)
- **Chaves de Cruzamento:** `codigo_cnes` + `competencia` (Ano+Mês de competência, ex: `201904`).
- **O Combate ao Data Leakage:** Um cruzamento convencional apenas pelo ID do hospital anexaria as características do hospital de 2025 (como número de UTIs atuais) a um paciente que infartou em 2015. O uso da `competencia` garante um pareamento em "máquina do tempo" perfeito, vinculando o paciente à infraestrutura real do hospital no mês exato da sua internação.

---

## 3. Seleção de Features e Redução de Dimensionalidade (Notebook 05)

### 3.1 Filtro de Data Leakage Conceitual
- **Variáveis Excluídas:** `motivo_saida`, `data_saida`, `cid_morte`, etc.
- **Motivo:** O objetivo do classificador de Machine Learning é estimar o risco exclusivamente no momento da entrada do paciente no hospital. Se o modelo consumisse a variável "motivo_saida" (cujo valor já diz se ele morreu ou teve alta), teríamos um vazamento de dados óbvio. Pelo mesmo princípio lógico, variáveis retrospectivas como `dias_permanencia`, `quantidade_diarias`, `uti_mes_total` e todas as associadas a `valor_` foram profilaticamente expurgadas antes do ML, pois elas representam o faturamento hospitalar consolidado apenas no fim da internação, atuando como oráculos do futuro.
- **Atenção Temporal:** Variáveis de datas brutas (como `ano_competencia`) foram retidas no NB05 apenas para servir de âncora para o particionamento temporal no NB06, onde sofreram *drop* imediatamente antes da separação *X/y*.

### 3.2 Eliminação de Constantes e Quasi-Constantes
- **Filtro de Variância (> 98%):** Variáveis cuja categoria majoritária preenche mais de 98% dos registros são deletadas.
- **Justificativa:** Em algoritmos baseados em entropia e ganho de informação (como Árvores de Decisão), variáveis estáticas não geram poder de corte e apenas adicionam custo computacional e risco de multicolinearidade.

### 3.3 Filtro de Textos e Alta Cardinalidade
- **Eliminação de > 100 categorias:** Graças à transição para textos (`object`) das categorias do SUS, o Notebook 05 captura corretamente descrições extremamente singulares e as dropa, impedindo que cheguem na etapa de *One-Hot Encoding* onde causariam o efeito *Curse of Dimensionality*.

---

## 4. Modelagem Preditiva e Machine Learning (Notebook 06)

### 4.1 Validação e Divisão dos Dados (Split Temporal)
- **Design de Train-Test:** Treino (2015 a 2022) e Teste (2023 a 2025).
- **Justificativa Científica (vs K-Fold Random):** Em dados de saúde baseados em histórico contínuo, utilizar K-Fold aleatório na base inteira permitiria que o modelo fosse treinado com um caso de 2025 e testado em um paciente de 2017. Isso se chama *Look-ahead bias*. O Split Temporal simula o ambiente real: usamos o passado para prever o futuro.

### 4.2 Tratamento do Desbalanceamento de Classes
A letalidade hospitalar por IAM na base está na faixa dos **9.38%**, configurando um claro desbalanceamento de classes (90.6% vs 9.4%).
- **XGBoost:** Utilização do hiperparâmetro `scale_pos_weight` calculado pela divisão aritmética de Altas por Óbitos no treino (~8.94). Isso força a função de perda (Loss Function) do XGBoost a penalizar quase 9 vezes mais o erro ao classificar erroneamente um óbito.
- **Random Forest:** Utilização de `class_weight='balanced'`, que ajusta o peso das amostras inversamente proporcional à frequência da classe.

### 4.3 Tunagem de Hiperparâmetros (Arquitetura)
- **Random Forest:** `n_estimators=300` (garante convergência e estabilidade das previsões votadas), `max_depth=12` (evita o *overfitting* agressivo padrão de florestas), `min_samples_leaf=5` (força a criação de nós mais robustos estatisticamente). `SimpleImputer(strategy='median')` acoplado ao *Pipeline* para preencher *NaNs* com a mediana do treino.
- **XGBoost:** `tree_method='hist'` (aceleração para grandes volumes em GPU/CPU), `learning_rate=0.05` (aprendizado suave e gradual para reduzir variância e evitar mínimos locais em dados médicos sensíveis), `max_depth=6` (focado em aprendizado iterativo curto), `subsample=0.8` (estocasticidade mitigadora de *overfitting*).

### 4.4 Validação Cruzada (CV) e Métrica de Avaliação
- Utilização de `StratifiedKFold` (5-folds) *estritamente dentro da partição de treino*.
- **Métrica Primária (ROC-AUC):** Com ~9.4% de letalidade, um modelo "burro" que sempre chute Alta teria ~90.6% de acurácia. A métrica Area Under the Receiver Operating Characteristic Curve (ROC-AUC) mensura a capacidade real do modelo de discriminar o risco relativo entre classes independentemente do *threshold* escolhido, sendo o padrão ouro em scores médicos.

---

## 5. Análise de Sobrevivência (Notebook 07)

Diferente do Machine Learning tradicional que estima apenas a ocorrência (Se), a análise de sobrevivência estima o *Quando* (O Tempo até o desfecho).

### 5.1 O Setup do Modelo
- **A Variável de Tempo ($T$):** Exclusivamente `dias_permanencia` (tempo total da internação do paciente, extraído de `quantidade_diarias`). Diferente de análises fragmentadas, o tempo total foi estritamente separado de variáveis de uso intensivo (covariáveis como `uti_mes_total`), garantindo que o $T$ do modelo de Cox represente fielmente o evento primário e não cause multicolinearidade temporal.
- **O Evento ($E$):** O óbito (Alta é contabilizada estatisticamente como *Censura à Direita*).

### 5.2 Curvas de Kaplan-Meier
- Estimador não paramétrico utilizado para desenhar a curva teórica de sobrevivência dos pacientes por subgrupos puros.
- **Teste de Log-Rank:** Realizado para validação de hipótese matemática. Caso $p < 0.05$, atesta-se rigorosamente que a velocidade e probabilidade de morte divergem estatisticamente de forma significativa entre os grupos comparados (ex: Masculino vs Feminino).

### 5.3 Regressão de Riscos Proporcionais de Cox
- O Modelo de Cox avalia o efeito multivariado simultâneo.
- **Hazard Ratio ($e^{coef}$):** Interpretação primária da análise. Valores $> 1$ indicam que a *feature* acelera a falha (risco mortífero), e valores $< 1$ funcionam como fatores de proteção no período longitudinal.
- **Validação de Premissa (Resíduos de Schoenfeld):** Modelos de Cox dependem da premissa de *Riscos Proporcionais* (O impacto da variável deve ser constante ao longo do tempo). O uso da métrica `proportional_hazard_test` do módulo `lifelines` expõe matematicamente caso haja uma falha estrutural de proporcionalidade (trend temporal), conferindo validação estatística inquestionável à análise.

