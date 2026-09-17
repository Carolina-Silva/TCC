# Auditoria Completa — O que Ainda Falta no TCC

> Levantamento baseado na leitura integral do PDF do template. Não inclui figuras, tabelas e o texto da seção SHAP (já tratados anteriormente).

---

## 🔴 Crítico — Placeholders explícitos no texto

### 1. `[FIGURA: diagrama de fluxo do pipeline]` — Metodologia, p. 4
Você assumiu que fará manualmente. ✅ Registrado — precisa criar e inserir.

---

### 2. `[CÓDIGO: trecho do merge final SIH × CNES]` — Metodologia, p. 6
O template pede explicitamente um bloco de código mostrando o merge final entre SIH e CNES com a chave composta hospital × mês.
> Notebook de origem: `02_etl_database_integration.ipynb`

**O que inserir:** O trecho de código do merge final — o `pd.merge()` com `left_on=['codigo_cnes', 'competencia']`, incluindo o comentário de que é um `left join` para preservar todas as internações.

---

### 3. `[CÓDIGO: split temporal e treinamento de um dos modelos]` — Metodologia, p. 8
O template pede um bloco de código ilustrativo do split temporal (2015–2022 treino / 2023–2025 teste) e do treinamento de pelo menos um modelo.
> Notebook de origem: `06_predictive_modeling.ipynb`

**O que inserir:** O trecho com a divisão por ano + o `fit()` de um dos modelos (XGBoost ou Logistic Regression).

---

### 4. `[X]` no limiar de correlação de Pearson — Metodologia, p. 7
> *"O filtro de correlação de Pearson entre cada atributo remanescente e a variável-alvo (|r| < **[X]**) foi aplicado..."*

**O que inserir:** O valor real do threshold de correlação usado no notebook `05_feature_selection.ipynb`. Verificar qual valor foi usado no código.

---

### 5. `[adicionar aqui alguns resultados que mostram o quanto tivemos de cada hospital]` — Metodologia, p. 6
> *"A soma dos três critérios originou quatro categorias: Baixa (escore 0), Média (escore 1), Alta (escore 2) e Muito Alta (escore 3). **[adicionar aqui alguns resultados que mostram o quanto tivemos de cada hospital]**"*

**O que inserir:** Os números reais de hospitais e internações por categoria de estrutura. Esses dados estão disponíveis no notebook `03b_hospital_quality_index.ipynb` e na figura `dist_estrutura_hospitalar.jpg` já gerada.

---

### 6. `[ SHAP ]` na Conclusão — p. 15
> *"...reforçando que a estratificação de risco realizada exclusivamente no momento da admissão... **[ SHAP ]**."*

Há um placeholder `[ SHAP ]` no meio da Conclusão que precisa de texto. Contexto: está no parágrafo que discute a insuficiência da estratificação de risco no momento da admissão.

**O que inserir:** Uma frase conectando a análise de sobrevivência com a descoberta SHAP. Sugestão:
> *"A análise de valores SHAP corroborou esse achado ao identificar que a idade e o tipo de procedimento realizado concentram a maior parte da capacidade preditiva do modelo, enquanto variáveis de infraestrutura hospitalar exercem influência secundária mas estatisticamente relevante sobre o desfecho, o que reforça a necessidade de modelos que integrem tanto o risco clínico quanto a capacidade estrutural do hospital no momento da admissão."*

---

## 🟡 Importante — Valores numéricos a preencher

### 7. Mediana de sobrevivência global (`x dias`) — Resultados, seção Sobrevivência
> *"A mediana de sobrevivência global foi de **x dias**..."*

**O que inserir:** Rodar o notebook `07_survival_analysis.ipynb` e extrair a mediana da curva KM global do output da célula KM global (ou da figura `km_global.jpg`).

---

### 8. Valores das AUC-ROC na Tabela de desempenho — Resultados
O PDF menciona AUC-ROC de 0,78 para o XGBoost na Conclusão, mas a tabela de resultados precisa conter os valores completos de todos os 4 modelos (CV + out-of-time). Verificar se a Tabela de AUC está preenchida com os números reais ou se ainda tem placeholders.

---

### 9. Hiperparâmetro do Random Forest: `max_features` — Metodologia, p. 8
O texto menciona os hiperparâmetros do XGBoost e do RF, mas não inclui `max_features` do RF nem `num_leaves` do LightGBM. Opcional, mas recomendável completar para consistência metodológica.

---

## 🟡 Importante — Seções de texto com conteúdo incompleto

### 10. Seção de Resultados: EDA inicial — figuras não citadas
As figuras abaixo foram geradas pelos notebooks mas **não têm parágrafo de citação no PDF**:
| Figura | Arquivo |
|--------|---------|
| Evolução temporal de internações | `eda_evolucao_temporal.jpg` |
| Distribuição etária por sexo | `eda_dist_etaria_sexo.jpg` |
| Desfecho hospitalar (barras %) | `eda_desfecho_hospitalar.jpg` |
| Custo × permanência (scatter) | `eda_custo_vs_permanencia.jpg` |
| Boxplot de permanência por desfecho | `boxplot_permanencia_desfecho.jpg` |
| Heatmap de correlação | `heatmap_correlacao.jpg` |
| Distribuição de estrutura hospitalar | `dist_estrutura_hospitalar.jpg` |

Se quiser incluí-las, cada uma precisa de pelo menos um parágrafo de citação antes da figura.

---

### 11. Seção de Resultados: curvas KM por faixa etária e por raça/cor
As figuras `km_faixa_etaria.jpg` e `km_raca_cor.jpg` foram geradas mas **não há texto descrevendo os resultados** desses log-rank tests no PDF. São subseções de Análise de Sobrevivência que estão implícitas mas sem texto.

---

### 12. Tabela 1 — CNES: colunas `Registros` incompletas
A Tabela 1 (p. 5) lista as 5 tabelas do CNES mas a coluna `Registros` está **vazia** (sem os números reais de registros de cada tabela). Esses valores precisam ser preenchidos com os totais reais baixados para São Paulo 2015–2025.

---

## 🔵 Menor prioridade — Elementos opcionais

### 13. Resumo / Abstract — palavras-chave
Verificar se as palavras-chave em português e inglês estão preenchidas (o PDF pode ter placeholders aqui dependendo da versão).

### 14. Agradecimentos — seção opcional
O template instrui que é opcional. Se quiser incluir, redija antes de enviar.

### 15. Referências — verificar completude
O template lista apenas uma referência de exemplo (Jayaprasad, 2016). As referências reais (Ribeiro et al. 2021, Précoma et al. 2019, Escosteguy et al. 2002, Cavalheiro et al. 2024, Koike 2025, Gioia et al. 2023) precisam estar formatadas conforme as normas MBA USP/Esalq no tópico Referências.

### 16. Apêndice — matrizes de confusão
As 4 matrizes de confusão individuais (por modelo) foram geradas mas não têm posição definida no PDF. Colocá-las em Apêndice é a opção mais limpa.

---

## Resumo de Prioridades

| # | Item | Prioridade | Origem dos dados |
|---|------|-----------|-----------------|
| 2 | `[CÓDIGO]` merge SIH×CNES | 🔴 | NB02 |
| 3 | `[CÓDIGO]` split + treinamento | 🔴 | NB06 |
| 4 | Valor `[X]` do threshold de correlação | 🔴 | NB05 |
| 5 | Nº de hospitais por categoria de estrutura | 🔴 | NB03b / fig |
| 6 | Texto `[ SHAP ]` na Conclusão | 🔴 | — (escrever) |
| 7 | Mediana de sobrevivência `x dias` | 🟡 | NB07 / KM global |
| 8 | Tabela AUC completa | 🟡 | NB06 output |
| 12 | Coluna Registros da Tabela 1 | 🟡 | NB01/02 |
| 10 | Parágrafos para figuras EDA não citadas | 🟡 | — (escrever) |
| 11 | Texto KM faixa etária e raça/cor | 🟡 | NB07 output |
| 15 | Referências formatadas | 🟡 | — |
| 13 | Palavras-chave | 🔵 | — |
| 14 | Agradecimentos | 🔵 | — (opcional) |
| 16 | Apêndice matrizes confusão | 🔵 | NB06 figures |
