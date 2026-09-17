# Análise Comparativa: Template PDF × Notebooks

> Comparação entre o que está descrito no texto do TCC (PDF) e o que está implementado nos notebooks.

---

## ✅ O que está ALINHADO (presente nos dois)

| Tema | PDF | Notebook |
|------|-----|----------|
| Download via FTP DATASUS e conversão `.dbc → .csv` | ✅ mencionado | ✅ `01a` |
| Tradução de códigos categóricos via dicionários `.def/.cnv` | ✅ mencionado + trecho de código | ✅ `01b` |
| Filtro por CID-10 I21 (IAM) e limpeza de nulos (>70% ausência) | ✅ detalhado | ✅ `02` |
| Integração SIH × CNES com chave hospital × mês/ano | ✅ enfatizado como diferencial metodológico | ✅ `02` + `03` |
| Escore de estrutura hospitalar (03b) | ✅ usado nos resultados | ✅ `03b` |
| EDA com taxa de letalidade, idade, tempo de permanência | ✅ resultados detalhados | ✅ `03` + `04` |
| Histograma de idade por desfecho | ✅ `[FIGURA]` explícita | ✅ `04` |
| Tabela descritiva (idade, permanência, sexo) separada por desfecho | ✅ `[TABELA]` explícita | ✅ `04` |
| Split temporal (treino 2015–2022 / teste 2023–2025) | ✅ mencionado | ✅ `06` |
| Anti-data-leakage (filtro de correlação só no treino, imputação só no treino) | ✅ mencionado | ✅ `05` + `06` |
| 4 modelos: Regressão Logística, Random Forest, XGBoost, LightGBM | ✅ nomeados com AUC | ✅ `06` |
| Validação cruzada StratifiedKFold 5-fold (só no treino) | ✅ resultados CV vs. out-of-time | ✅ `06` |
| Curva ROC comparativa dos 4 modelos | ✅ `[FIGURA]` | ✅ `06` |
| Tabela AUC-ROC CV vs. teste out-of-time | ✅ `[TABELA]` | ✅ `06` |
| SHAP summary plot (interpretabilidade) | ✅ `[FIGURA]` | ✅ `06` |
| Análise de interação: tercis de risco × estrutura hospitalar | ✅ seção inteira | ✅ `06` |
| Teste qui-quadrado + Likelihood Ratio Test (interação) | ✅ resultados χ²(11)=8371 e LR(6)=50,99 | ✅ `06` |
| Análise de Fairness (SHAP por sexo e raça/cor) | ✅ citado na conclusão `[SHAP]` | ✅ `06` |
| Kaplan-Meier global + estratificado (sexo, faixa etária, raça/cor, estrutura) | ✅ resultados com p-valores | ✅ `07` |
| Regressão de Cox (HR com IC 95%) | ✅ HR=1,72 urgência, C-statistic=0,65 | ✅ `07` |
| Teste de Schoenfeld (premissa riscos proporcionais) | ✅ p-valores por covariável | ✅ `07` |

---

## ⚠️ O que está no PDF mas **incompleto ou ausente** nos notebooks

### 1. 🔴 Diagrama de fluxo do pipeline (Figura obrigatória na Metodologia)
**PDF:** Há um marcador explícito:
> `[FIGURA: diagrama de fluxo do pipeline DATASUS FTP → conversão .dbc/.csv → tradução de códigos → limpeza SIH → integração CNES → seleção de features → split temporal → modelagem/SHAP → análise de interação → sobrevivência]`

**Notebooks:** Nenhum dos notebooks gera esse diagrama de fluxo. É um `[FIGURA]` placeholder no texto — a **imagem ainda não existe** e precisa ser criada (pode ser Mermaid, draw.io, matplotlib, etc.) e exportada para `reports/figures/`.

---

### 2. 🔴 Tabela 1 (descrição das tabelas do CNES) com número de registros
**PDF:** Aparece explicitamente na Metodologia com os dados:

| Tabela | Sigla | Conteúdo | Registros |
|--------|-------|----------|-----------|
| Estabelecimentos | ST | Dados cadastrais | 62.522 |
| Equipamentos | EQ | Equipamentos existentes | 552.840 |
| Habilitações | HB | Habilitações/certificações | 1.471.830 |
| Leitos | LT | Quantidade por tipo | 2.219.516 |
| Serviços Especializados | SR | Serviços ofertados | 427.109 |

**Notebooks:** Os notebooks `01a` e `02` coletam e processam essas bases, mas **nenhum notebook imprime ou exporta essa tabela de contagem de registros** para documentação. Os números provavelmente existem nos dados — precisam ser extraídos e documentados formalmente.

---

### 3. 🟡 Tabela de AUC-ROC CV vs. out-of-time (formatada para o TCC)
**PDF:** 
> `[TABELA: AUC-ROC CV (treino) vs. teste out-of-time para os quatro modelos]`
> Com valores explícitos: XGBoost 0,7940→0,7826; LightGBM 0,7930→0,7794; RF 0,7649; Log. 0,7534→0,7227

**Notebooks (`06`):** A validação cruzada é executada e as métricas são impressas, mas **não há uma célula que consolide e formate essa tabela comparativa final** (CV vs. out-of-time, os 4 modelos lado a lado) pronta para copiar para o TCC.

---

### 4. 🟡 Seção "Interpretabilidade e Justiça Algorítmica" — discussão textual ausente
**PDF:** 
> `Interpretabilidade e Justiça Algorítmica`  
> `[FIGURA: SHAP summary plot]`

A seção existe no PDF mas está **sem texto de discussão** — apenas o placeholder da figura. O notebook `06` gera os plots de SHAP e de fairness por sexo e raça, mas a **narrativa de interpretação dos resultados** (quais variáveis dominam, o que o SHAP revela sobre o modelo, se há disparidade por grupo) ainda precisa ser escrita no documento.

---

### 5. 🟡 Valores específicos da análise de sobrevivência (mediana KM)
**PDF:**
> `a curva de Kaplan-Meier revelou uma mediana de sobrevivência hospitalar de **x dias**`

O `x` está como placeholder — o notebook `07` gera a curva, mas **o valor da mediana global ainda não foi preenchido no texto**. Pequena inconsistência entre notebook (executa e plota) e PDF (resultado não consolidado).

---

### 6. 🟡 Teste de DeLong entre modelos
**PDF:** 
> `A aplicação do teste de DeLong confirmou diferença estatisticamente significativa (z = 5,25; p = 1,51×10⁻⁷)`

**Notebooks (`06`):** O notebook tem a **seção 4.1 dedicada ao Teste de DeLong** com código pronto. Os resultados numéricos no PDF indicam que a análise foi executada — mas vale confirmar se o output do teste está sendo exportado/salvo de forma organizada ou apenas impresso no console.

---

### 7. 🟢 Seleção de features — critério de 70% vs. 99% de ausência
**PDF (Metodologia):**  
> `colunas com proporção de valores ausentes superior a 70% foram removidas`

**Notebook `05` (Seleção de Features — Etapa 5):**  
> Remove colunas com `> 99%` de ausência

São **dois critérios diferentes para etapas diferentes**: o de 70% é aplicado na ETL inicial (notebook `02`), o de 99% é aplicado na seleção final de features (notebook `05`). Isso está correto e consistente, mas pode causar confusão no leitor do TCC. Seria bom deixar **explícito no texto do PDF** que os dois filtros são aplicados em momentos diferentes do pipeline.

---

## 🔵 O que está nos notebooks mas **não aparece no PDF**

### 8. 🔵 Notebook `03b` — Índice de Qualidade Hospitalar
O `03b` implementa um **escore composto de estrutura hospitalar** com metodologia detalhada (pesos, componentes, categorização em Baixa/Média/Alta/Muito Alta). O PDF usa o resultado (`escore_estrutura`) nos Resultados e Discussão, mas **não descreve a metodologia de construção do índice na seção de Metodologia**.

➡️ O PDF deveria ter um parágrafo explicando como o escore foi construído (variáveis usadas, pesos, categorias).

---

### 9. 🔵 Notebook `04` — Visualizações completas da EDA
O `04` gera 4 figuras (`hist_idade.jpg`, `boxplot_permanencia_desfecho.jpg`, `barras_letali_faixa_etaria.jpg`, `heatmap_correlacao.jpg`) e tabelas de contingência detalhadas por variável qualitativa.

No PDF:
- O histograma de idade aparece: ✅ `[FIGURA: distribuição de idade por desfecho]`
- A tabela descritiva aparece: ✅ `[TABELA: estatísticas descritivas]`
- O **boxplot de permanência**, a **figura de letalidade por faixa etária** e o **heatmap de correlação** — **não têm marcadores `[FIGURA]` no PDF**. Estão sendo gerados mas provavelmente não estão sendo inseridos no texto.

---

### 10. 🔵 Notebook `03` — 4 gráficos da EDA inicial
O `03` gera 4 gráficos (evolução temporal, distribuição etária por sexo, desfecho hospitalar, custo × permanência). Nenhum desses aparece como `[FIGURA]` no PDF (o PDF pula direto para os resultados da EDA com os valores finais).

---

## 📋 Resumo Executivo

| Prioridade | Item | Ação necessária |
|-----------|------|----------------|
| 🔴 Alta | Diagrama de fluxo do pipeline | Criar e exportar a figura — não existe em nenhum notebook |
| 🔴 Alta | Metodologia de construção do escore hospitalar (03b) | Adicionar parágrafo no PDF descrevendo os componentes e pesos |
| 🟡 Média | Tabela AUC-ROC comparativa consolidada | Criar célula no `06` que exporte a tabela formatada |
| 🟡 Média | Mediana global do KM (valor `x` dias) | Preencher o placeholder no PDF com o valor real do notebook `07` |
| 🟡 Média | Discussão textual do SHAP / Fairness | Escrever a interpretação dos resultados no PDF |
| 🟡 Média | Dois critérios de ausência (70% vs 99%) | Esclarecer no PDF que são etapas distintas do pipeline |
| 🟢 Baixa | Boxplot, heatmap correlação, faixa etária | Inserir `[FIGURA]` correspondente no texto do PDF |
| 🟢 Baixa | 4 gráficos da EDA inicial (03) | Decidir se entram no PDF ou ficam apenas nos notebooks |
| 🟢 Baixa | Tabela de contagem de registros CNES | Verificar se os números do PDF batem com o que foi processado |
