# Relatório Final de Resultados e Métricas do Pipeline

> **TCC — MBA em Data Science e Analytics**  
> **Tema:** Predição de Letalidade Hospitalar por IAM no SUS utilizando Machine Learning e Análise de Sobrevivência  
> **Escopo:** Estado de São Paulo (2015 a 2025)

Este documento compila rigorosamente todas as métricas resultantes do processamento da orquestração final de dados. Ele serve como consulta rápida e oficial para os números que devem constar no capítulo de "Resultados" da sua monografia.

---

## 1. O Funil de Extração de Dados (ETL)

A etapa de integração da base do SIH obedeceu a um forte filtro de seleção da coorte focado especificamente no Infarto Agudo do Miocárdio (CID-10: `I21`).

### Filtro Principal (SIH)
* **Registros Brutos Iniciais (SP 2015–2025):** 28.284.570 internações.
* **Registros Pós-Filtro IAM (CID I21):** 416.027 internações.
* **Percentual de retenção (Prevalência hospitalar do IAM):** 1,47%.
* **Percentual filtrado:** 98,53%.

### Exclusão Pediátrica
* **Registros pediátricos removidos (Idade < 18 anos):** 660.
* **Base Final de Internações de Adultos:** **415.367** registros.

---

## 2. A Base CNES e o Merge Longitudinal

A captura da infraestrutura hospitalar baseada no mês exato da ocorrência do infarto foi um sucesso técnico massivo.

* **Fotos Hospitalares Únicas Capturadas (CNES):** 62.552 registros mensais de hospitais ativos.
* **Hospitais Distintos (CNES Únicos que atenderam IAM):** 506 estabelecimentos.
* **Colunas Totais do CNES após Pivoteamento e Integração:** 627 colunas.
* **Limpeza de Nulos no CNES:** 35 colunas foram deletadas por apresentarem mais de 70% de dados ausentes (Ex: `data_publicacao_contrato_municipal_cod`).
* **Taxa de Sucesso do Cruzamento (Match Rate SIH x CNES):** **100,00%** (Absolutamente todos os 415.367 infartados encontraram o correspondente infraestrutural do seu hospital naquele mês exato).

---

## 3. Análise Exploratória, Demografia e Desfecho Clínico

Com a base consolidada, mapeamos a clínica e a letalidade bruta do Infarto Agudo do Miocárdio em hospitais públicos do estado de São Paulo durante esta década.

### Desfecho Primário
* **Nº Total de Internações (Pacientes Adultos):** 415.367
* **Desfecho ALTA:** 376.410 (90,62%)
* **Desfecho ÓBITO:** 38.957 (9,38%)
* **TAXA DE LETALIDADE HOSPITALAR GERAL:** **9,38%**

### Estatísticas Demográficas da População
* **Idade:**
  * **Média:** 62,81 anos
  * **Mediana:** 63,0 anos
  * **Amplitude:** de 18 a 99 anos
  * **Desvio-padrão:** 12,33 anos
* **Tempo de Permanência Hospitalar Pura (Data Saída - Data Internação, variável `dias_permanencia`):**
  * **Média:** 7,18 dias
  * **Mediana:** 4,0 dias
* **Quantidade de Diárias Faturadas (variável `quantidade_diarias`):**
  * **Média:** 5,67 dias
  * **Mediana:** 3,0 dias
  * **Terceiro Quartil (Q3):** 7,0 dias
  * **Limitação Citável:** A diferença sistemática (~1 dia) entre o tempo real da internação e o tempo faturado reflete a convenção administrativa do SIH/SUS. O modelo de Sobrevivência (Cox/KM) utilizou estritamente o tempo de permanência puro (`dias_permanencia`).

---

## 4. O Funil de Seleção de Features (Dimensionality Reduction)

O pipeline aplicou a metodologia de eliminação estrita para evitar o *Curse of Dimensionality* (Maldição da Dimensionalidade) e o vazamento de dados, reduzindo as características hospitalares a apenas os preditores de alto valor.

* **Colunas Iniciais Pós-Merge:** 660 variáveis.
* **Etapa 1 (Data Leakage):** Remoção de colunas conceituais proibidas como datas futuras e `motivo_saida` (**- 24 colunas**).
* **Etapa 2 (Constantes Matemáticas):** Remoção de variáveis que possuíam o mesmo valor na base inteira (**- 60 colunas**).
* **Etapa 3 (Quasi-constantes > 98%):** Remoção agressiva de variáveis altamente enviesadas onde 98% dos hospitais tinham a mesma marcação (**- 133 colunas**).
* **Etapa 5 (Textos Puros de Alta Cardinalidade):** Exclusão de strings complexas não computáveis (Ex: IDs brutos) (**- 7 colunas**).
* **Etapa 4 (Alocação Dinâmica para o ML):** O filtro de Correlação de Pearson com o alvo (`|r| < 0.03`) foi removido desta etapa preliminar e movido exclusivamente para o Treino (Pós-Split) para erradicar o *Data Leakage*.

**O Funil Tridimensional de Features (Pré e Pós Encoding):**
1. Dimensionalidade Clínica Original (Notebook 05): **436 colunas de ouro**.
2. Dimensionalidade Expandida pós-*One-Hot Encoding* (Notebook 06): **520 colunas binárias e numéricas**.
3. **Dimensionalidade Final de Predição** (Após Etapa 4 de Correlação): **234 features estritamente validadas**.

---

## 5. Performance Preditiva de Machine Learning

Ao utilizar o *Split Temporal* (Treino em 2015-2022 e Teste em 2023-2025), garantimos a imunidade absoluta contra *Look-ahead bias*. O modelo precisou prever o futuro "no escuro". O balanço matemático foi crucial para lidar com a minoria do óbito (9.38%).

* **Base de Treino (2015 a 2022):** 277.487 internações (10,06% de óbitos).
* **Base de Teste Out-of-Time (2023 a 2025):** 137.880 internações cegas (8,01% de óbitos).

### Resultados no Conjunto de Teste Out-of-Time (2023–2025)
A avaliação final no conjunto de teste comprovou a robustez dos modelos no cenário clínico realista (medidos pela ROC-AUC e sensibilidade/recall na classe minoritária com threshold = 0.50).

* **XGBoost:** **AUC = 0,7826** | Recall Óbitos: **66,81%**
* **LightGBM:** **AUC = 0,7794** | Recall Óbitos: **68,09%**
* **Random Forest:** AUC = 0,7649 | Recall Óbitos: 64,22%
* **Regressão Logística (Baseline):** AUC = 0,7227 | Recall Óbitos: 68,19%

> **Nota Metodológica (Hiperparâmetros):** O LightGBM operou com `n_estimators=300, max_depth=6, learning_rate=0.05, num_leaves=63, min_child_samples=20`. A Regressão Logística utilizou `max_iter=1000`. Todos usaram `class_weight='balanced'`.

### Resultados da Métrica ROC-AUC na Validação Cruzada (K-Fold 5 de Treino)
* **XGBoost:** AUC = 0,7940 ± 0.0022
* **LightGBM:** AUC = 0,7930 ± 0.0016
* **Random Forest:** AUC = 0,7747 ± 0.0026
* **Regressão Logística:** AUC = 0,7534 ± 0.0040

### Teste de DeLong (Validação Estatística das Diferenças de AUC)
As curvas ROC não foram julgadas apenas "a olho". O Teste de DeLong provou se a diferença entre os algoritmos foi matemática ou ao acaso:
* **XGBoost vs LightGBM:** A vitória do XGBoost sobre o LightGBM é comprovada estatisticamente (`z = 5.25`, **`p-value = 1.50e-07`***).
* **XGBoost vs Regressão Logística:** O XGBoost domina a AUC com margem inquestionável (`p-value = 0.00`***).

**Conclusão Clínica ML:** Após a extirpação profilática do Data Leakage (retirada do tempo e faturamento), a predição retornou ao patamar realista das bases estritamente administrativas, desprovidas de marcadores biológicos. O **XGBoost** demonstrou a melhor capacidade de discriminação geral (AUC 0.78), enquanto a **Regressão Logística** e o **LightGBM** balancearam a maior capacidade de capturar a mortalidade com o threshold basal (Recall > 68%).

### Interpretabilidade Global (SHAP Values)
A abstração das *black-boxes* (caixas pretas) dos modelos de árvore foi resolvida utilizando a Teoria dos Jogos (Valores SHAP). Retirando as variáveis "espiãs" do futuro, os maiores preditores matemáticos determinantes do Risco de Óbito identificados na admissão do paciente foram:

1. **Idade do Paciente (`idade`):** Confirma a vulnerabilidade geriátrica como fator primário inflexível.
2. **Complexidade do Procedimento (`procedimento_realizado`):** Cirurgias hemodinâmicas versus tratamento conservador indicam o grau da oclusão e o risco cirúrgico.
3. **Comorbidades Associadas (`tipo_diag_sec_2` e `tipo_diag_sec_3`):** Doenças pré-existentes diagnosticadas secundariamente exacerbam o desfecho primário.
4. **Caráter de Urgência (`carater_internacao_Urgência`):** Entradas emergenciais carreiam mortalidade basal sistemicamente superior a agendamentos controlados.
5. **Infraestrutura Hospitalar (`possui_unidade_neonatal`, `leitos_...`):** Variáveis de estrutura hospitalar operando como proxy da capacidade de resposta intensiva da unidade.

---

## 6. Resultados da Análise de Sobrevivência (Notebook 07)

A análise focada no tempo longitudinal até o desfecho revelou o perfil mortífero da patologia a longo prazo na rede pública.

### Curvas de Kaplan-Meier
* **Mediana Global de Sobrevivência ao Infarto:** **115,0 dias** (No estado de São Paulo, o paciente internado por IAM atinge a sobrevida pós-trauma aos 115 dias em ambiente intra-hospitalar).
  * *Ressalva:* Devido à baixa letalidade de eventos finais no 115º dia (a vasta maioria das mortes e altas ocorre na primeira semana), o número de pacientes *"em risco"* nesta janela temporal é exíguo. A estimativa nos extremos da curva possui um longo intervalo de confiança.
* **Teste de Log-Rank por Sexo:** A diferença de sobrevivência entre pacientes do sexo Masculino e Feminino foi testada rigorosamente, retornando um **`p-value = 2.97e-150`** (uma diferença estatisticamente avassaladora a favor de trajetórias distintas por sexo).

### Regressão de Riscos Proporcionais de Cox
O modelo multivariado calculou os fatores que aceleram ou freiam o risco diário de morte. A métrica **Hazard Ratio (HR)** revela o impacto direto:
* **Idade:** HR = 1,05 (Cada ano adicional de vida aumenta o risco de óbito em 5%).
* **Sexo (Masculino):** HR = 1,13 (Homens apresentam um risco 13% maior em relação às mulheres no longo prazo).
* **Uso de UTI:** HR = 1,72 (A necessidade de cuidados intensivos eleva o risco letal em 72%).
* **Caráter de Urgência:** HR = 1,75 (Entradas via emergência possuem um risco letal 75% maior comparadas às eletivas).

* **Concordance Index (C-Statistic):** **0,6716** (Capacidade do modelo de ordenar temporalmente os óbitos com as features limitadas utilizadas).
* **Resíduos de Schoenfeld (Validação da Premissa Crítica):**
  * O teste checa se os riscos se mantêm proporcionais ao longo do tempo.
  * O `carater_internacao` passou no teste (`p-value = 0.59`), provando que a urgência mantém o mesmo peso letal fixo durante toda a internação. O HR de 1,75 é totalmente confiável e constante.
  * As variáveis `idade` (`p = 1.18e-66`), `sexo` (`p = 0.02`) e `uso_uti` (`p = 0.00`) **violaram a premissa**. Isso indica clinicamente que o peso dessas variáveis muda dependendo da fase da internação (ex: o impacto da idade na mortalidade do 1º dia é diferente do impacto no 30º dia). Logo, os HRs calculados de 1,05, 1,13 e 1,72 representam um *efeito médio da vida da internação*, e não um risco constante dia a dia.

---

> Base de dados final do ciclo. As evidências matemáticas obtidas nestes notebooks certificam o cruzamento com qualidade impecável e endossam o poder dos modelos de IA não apenas como balizadores teóricos, mas como ferramentas tangíveis na predição imediata do agravamento do infarto na saúde pública paulista.
