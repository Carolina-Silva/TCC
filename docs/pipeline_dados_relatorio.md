# Relatório Técnico — Pipeline de Dados
## Predição de Letalidade Hospitalar por IAM no SUS

> **TCC — MBA em Data Science e Analytics**
> **Fonte:** DATASUS (SIH e CNES) — Estado de São Paulo — 2015 a 2025
> **CID-10:** I21 — Infarto Agudo do Miocárdio
> **Última atualização:** 01/09/2026

---

## Visão Geral do Pipeline

**Orquestrador Automático:** `run_pipeline.py` (executa os notebooks em cadeia, com suporte a *skip* de etapas custosas).

```
DATASUS FTP
    │
    ▼
[NB 01A] Coleta + Conversão  →  data/raw/  |  data/input/
    │
    ▼
[NB 01B] Tradução de Códigos  →  data/interim/*_traduzido.csv   (726 arquivos)
    │
    ▼
[NB 02]  ETL — Limpeza SIH + Integração CNES  →  sih_iam_modelagem.csv  |  cnes_hospitais_modelagem.csv
    │
    ▼
[NB 03]  Merge Longitudinal (Hospital × Mês)  →  data/processed/base_modelagem.csv
    │
    ▼
[NB 04]  EDA e Visualizações  →  reports/figures/
    │
    ▼
[NB 05]  Seleção de Features  →  data/processed/base_modelagem_reduzida.csv
    │
    ▼
[NB 06]  Modelagem Preditiva ML + SHAP  →  reports/figures/
    │
    ▼
[NB 07]  Análise de Sobrevivência (Cox/KM)  →  reports/figures/
```

---

## Notebook 01A — Coleta e Conversão de Dados Brutos

**Arquivo:** `01a_data_collection.ipynb`
**Outputs:** `data/raw/SIH/` · `data/raw/CNES/` · `data/input/SIH/` · `data/input/CNES/`

### 1.1 Coleta do SIH

| Parâmetro | Valor |
|-----------|-------|
| Estados | SP |
| Anos | 2015–2025 |
| Meses | 1–12 (todos os meses) |
| Arquivos gerados em `.dbc` | 121 |
| Arquivos convertidos para `.csv` | 121 |

Os arquivos SIH seguem o padrão `RDSP{AA}{MM}.dbc` (ex: `RDSP1501.dbc`).

### 1.2 Coleta do CNES

| Parâmetro | Valor |
|-----------|-------|
| Estados | SP |
| Anos | 2015–2025 |
| Meses | 1–12 |
| Bases | ST, LT, EQ, HB, SR |
| Arquivos gerados em `.dbc` | ~660 |
| Arquivos convertidos para `.csv` | 540 |

| Sigla | Descrição | Relevância para IAM |
|-------|-----------|---------------------|
| **ST** | Estabelecimentos (tabela mestre) | Tipo de unidade, natureza jurídica, localização |
| **LT** | Leitos por especialidade | Leitos cirúrgicos, clínicos, UTI |
| **EQ** | Equipamentos | Hemodinâmica, tomografia, ressonância |
| **SR** | Serviços Especializados | Cardiologia, UTI coronariana |
| **HB** | Habilitações | Certificações de alta complexidade cardiovascular |

### 1.3 Conversão .dbc → .csv

```
.dbc  →  descompressão (.dbf temporário)  →  leitura iso-8859-1  →  exportação .csv utf-8
```

Script: `src/utils/converter_dbc_para_csv.py` via `converter_dbc_para_csv_lote()`.

---

## Notebook 01B — Tradução de Códigos das Tabelas

**Arquivo:** `01b_data_translation.ipynb`
**Input:** `data/input/SIH/` e `data/input/CNES/`
**Output:** `data/interim/*_traduzido.csv` — **732 arquivos traduzidos**

### 2.1 Download dos Dicionários TabWin

Os dicionários `.def` e `.cnv` são baixados do FTP do DATASUS e salvos em `data/external/`:

```
data/external/SIH/         →  RDSP*.def  +  CNV/*.cnv
data/external/CNES/        →  Estabelecimento.def, Habilitacao.def, etc.  +  CNV/*.cnv
```

### 2.2 Sistema de Tradução

```
arquivo .DEF  →  mapeia: coluna → arquivo .CNV
arquivo .CNV  →  mapeia: código → descrição legível
```

Para cada coluna com dicionário, é gerada uma coluna `COLUNA_DESC` ao lado da original.

**Arquivos `.def` por tabela CNES:**

| Sigla | Arquivo .def |
|-------|-------------|
| HB | `Habilitacao.def` |
| LT | `Leitos_Especialidade.def` |
| EQ | `Equipamento.def` |
| SR | `Servico_Especializado_200803_.def` |
| ST | `Estabelecimento.def` |

### 2.3 Tradução em Lote com Multiprocessamento

A tradução completa (726 arquivos) é executada em paralelo usando todos os núcleos da CPU:

```python
with concurrent.futures.ProcessPoolExecutor() as executor:
    resultados = list(executor.map(processar_arquivo, tarefas))
```

- **726 arquivos** processados em paralelo (CNES + SIH)
- Arquivos já existentes em `data/interim/` são pulados automaticamente (idempotente)
- Nomes de saída: `cnes_{tipo}_{stem}_traduzido.csv` e `sih_{stem}_traduzido.csv`

> **Nota:** O CNES-EQ não possui mapeamento `.cnv` — as colunas `_DESC` ficam vazias para essa tabela (comportamento esperado).

---

## Notebook 02 — ETL: Limpeza do SIH e Integração do CNES

**Arquivo:** `02_etl_database_integration.ipynb`
**Input:** `data/interim/*_traduzido.csv`
**Outputs:**
- `data/interim/sih_iam.csv` — base completa com colunas `_cod`
- `data/interim/sih_iam_modelagem.csv` — base para modelagem sem `_cod`
- `data/interim/cnes_hospitais.csv` — CNES completo com colunas `_cod`
- `data/interim/cnes_hospitais_modelagem.csv` — CNES para modelagem sem `_cod`

### 3.1 Carregamento e Limpeza do SIH

Leitura em **chunks de 50.000 linhas** com filtro CID I21 aplicado durante a leitura:

```python
mask = (
    chunk["diagnostico_principal"].str.startswith("I21") |
    chunk["diagnostico_secundario"].str.startswith("I21")
)
```

**Limpeza aplicada:**

| Operação | Critério |
|----------|----------|
| Nulos em texto | Strings `""`, `"000"`, `"0000"` → `NaN` (apenas colunas object, exceto `_cod`) |
| Tipagem | Colunas `data_*` → datetime · `valor_*`, `quantidade_*`, `diarias_*` → float |
| Remoção de colunas | > 70% de nulos (−57 colunas) |
| Filtro etário | Adultos ≥ 18 anos (−660 registros pediátricos) |

**Resultado SIH:**

| Métrica | Valor |
|---------|-------|
| Internações brutas SIH (SP/2015–2025) | > 28.284.570 |
| Internações IAM (CID I21) | **416.027** |
| Adultos ≥ 18 | 415.367 (−660 pediátricos) |
| Colunas finais | **106** |
| `sih_iam.csv` (com `_cod`) | 415.367 registros |
| `sih_iam_modelagem.csv` (sem `_cod`) | 415.367 registros |

> **Novidade em relação à versão anterior:** a base SIH agora abrange **2015–2025** (11 anos, todos os meses), resultando em **415.367 internações por IAM** — versus 48.977 da versão com dados apenas de 2025.

### 3.2 Estratégia de Exportação Dupla (SIH e CNES)

Para cada base são geradas **duas versões**:
- **Completa** (`sih_iam.csv`, `cnes_hospitais.csv`): mantém colunas `_cod` para rastreabilidade e análises ad-hoc
- **Modelagem** (`sih_iam_modelagem.csv`, `cnes_hospitais_modelagem.csv`): remove colunas redundantes `_cod` para evitar multicolinearidade. Essa etapa derruba o número final de colunas do SIH de 121 para **97 colunas**, e as do CNES de 592 para **561 colunas**.

### 3.3 Carregamento e Integração do CNES

Filtro anti-OOM ("hospitais VIP"): apenas os **506 hospitais** que aparecem no SIH-IAM são carregados das tabelas CNES — evita carregar todos os ~120k hospitais do Brasil:

```python
cnes_vip = set(df_iam['codigo_cnes'].unique())  # 506 hospitais
df_st = load_cnes_custom('st', arquivos_cnes, cnes_vip)
```

**Registros carregados por tabela CNES:**

| Tabela | Registros | Colunas |
|--------|-----------|---------|
| ST (Estabelecimentos) | 62.552 | 259 |
| LT (Leitos) | 506.308 | 41 |
| EQ (Equipamentos) | 1.348.296 | 43 |
| SR (Serviços) | 2.025.992 | 46 |
| HB (Habilitações) | 390.787 | 49 |

**Pivot das tabelas secundárias** (chave: `codigo_cnes` + `competencia`):

| Tabela | Estratégia | Colunas geradas |
|--------|-----------|-----------------|
| LT | `pivot_table` — soma de `quantidade_leitos_existentes` | `leitos_<tipo>` · 4 tipos |
| EQ | `pivot_table` — soma de `quantidade_em_uso` | `equip_<codigo>` · 97 equipamentos |
| SR | `pivot_table` — flag `max` (0/1) | `servico_<codigo>` · 64 serviços |
| HB | `pivot_table` — flag `max` (0/1) | `habilitacao_<codigo>` · 211 habilitações |

**Resultado CNES após merge e limpeza:**

| Métrica | Antes | Após limpeza (> 70% nulos) |
|---------|-------|---------------------------|
| Hospitais (linhas) | 62.552 | 62.552 |
| Colunas | 627 | **592** (−35 colunas) |

**Distribuição de nulos antes da limpeza:**

| Faixa | Colunas |
|-------|---------|
| 100% | 25 |
| 70–99% | 24 |
| 50–69% | 11 |
| 1–49% | 18 |
| 0% (completas) | 549 |

---

## Notebook 03 — Merge Longitudinal e EDA

**Arquivo:** `03_merge_and_eda.ipynb`
**Input:** `data/interim/sih_iam_modelagem.csv` · `data/interim/cnes_hospitais_modelagem.csv`
**Output:** `data/processed/base_modelagem.csv`

### 4.1 Dimensões das bases carregadas

| Base | Registros |
|------|-----------|
| SIH-IAM | **415.367** internações |
| CNES | **62.552** fotos hospitalares (meses) |

### 4.2 EDA Exploratória Inicial

Visualizações geradas antes do merge:
1. **Evolução temporal do IAM por ano** — série histórica 2015–2025
2. **Distribuição de idade** por desfecho (óbito vs. alta)
3. **Distribuição de sexo** (`Feminino` / `Masculino` — já traduzidos)
4. **Distribuição do desfecho** (óbito vs. alta)

### 4.3 Chave Longitudinal — Hospital × Mês

**Grande mudança arquitetural:** o merge agora é feito usando **duas chaves**: `codigo_cnes` **+** `competencia` (YYYYMM), garantindo que a infraestrutura hospitalar reflita a **foto do mês exato da internação** — eliminando data leakage temporal.

```python
df_sih['competencia'] = df_sih['ano_competencia'] + df_sih['mes_competencia']

df_sih['codigo_cnes']  = df_sih['codigo_cnes'].astype(str).str.strip().str.zfill(7)
df_sih['competencia']  = df_sih['competencia'].astype(str).str.strip()

df_cnes['codigo_cnes'] = df_cnes['codigo_cnes'].astype(str).str.strip().str.zfill(7)
df_cnes['competencia'] = df_cnes['competencia'].astype(str).str.strip()
```

### 4.4 Merge (Left Join Hospital × Mês)

```python
df_base_modelagem = pd.merge(
    df_sih,
    df_cnes,
    on=['codigo_cnes', 'competencia'],
    how='left',
    suffixes=('', '_cnes')
)
```

**Resultado do merge:**

| Métrica | Valor |
|---------|-------|
| Linhas antes do merge | 415.367 |
| Linhas após o merge | **415.367** (sem duplicação) |
| Colunas após o merge | **660 colunas** (97 SIH + 561 CNES + 2 chaves sobrepostas) |
| Match rate (IAM → CNES) | **100,00%** |
| Arquivo gerado | `data/processed/base_modelagem.csv` |

> O match rate de 100,00% confirma que praticamente todas as internações encontraram o snapshot hospitalar do mês correspondente na base CNES. Os 0,08% sem correspondência são hospitais com dados CNES ausentes naquele mês específico.

---

## Resumo Consolidado do Pipeline

| # | Etapa | NB | Input | Output | Registros-chave |
|---|-------|----|-------|--------|-----------------|
| 1 | Coleta SIH (FTP) | 01A | DATASUS FTP | `data/raw/SIH/` | 121 arquivos `.dbc` |
| 2 | Conversão SIH | 01A | `data/raw/SIH/` | `data/input/SIH/` | 121 CSVs |
| 3 | Coleta CNES (FTP) | 01A | DATASUS FTP | `data/raw/CNES/` | ~660 arquivos `.dbc` |
| 4 | Conversão CNES | 01A | `data/raw/CNES/` | `data/input/CNES/` | 540 CSVs |
| 5 | Tradução de códigos | 01B | `data/input/` + `.def/.cnv` | `data/interim/*_traduzido.csv` | 726 arquivos |
| 6 | Limpeza SIH + filtro IAM | 02 | `sih_*_traduzido.csv` | `sih_iam_modelagem.csv` | **415.367** registros · 106 colunas |
| 7 | Integração CNES (5 tabelas) | 02 | `cnes_*_traduzido.csv` | `cnes_hospitais_modelagem.csv` | 62.552 hospitais · 592 colunas |
| 8 | Merge longitudinal | 03 | `sih_iam` + `cnes_hospitais` | `base_modelagem.csv` | 415.367 × match 100,00% |
| 9 | EDA Profunda | 04 | `base_modelagem.csv` | Gráficos | Exportação de Histograma e Boxplot |
| 10 | Feature Selection | 05 | `base_modelagem.csv` | `base_modelagem_reduzida.csv` | Filtros de Leakage e Constantes |
| 11 | Predição ML | 06 | `base_reduzida` | Métricas | Treino com Split Temporal e SHAP |
| 12 | Sobrevivência | 07 | `base_modelagem.csv` | Gráficos/Testes | Curvas de Kaplan-Meier e Regressão de Cox |

### Comparativo com versão anterior

| Dimensão | Versão anterior | Versão atual |
|----------|----------------|--------------|
| Período SIH | Jan–Dez 2025 (1 ano) | 2015–2025 (**11 anos**) |
| Meses coletados | 1–10, 12 (sem novembro) | **1–12** (todos) |
| Internações IAM | 48.977 | **415.367** |
| Hospitais VIP | 393 | **506** |
| Chave de merge | `codigo_cnes` | `codigo_cnes` + **`competencia`** |
| Granularidade CNES | Snapshot único (Dez/2025) | **Foto mensal** (por mês de internação) |
| Notebooks de coleta | 1 (NB01) | **2 (NB01A + NB01B)** |
| Tradução em lote | Sequencial | **Multiprocessamento (todos os CPUs)** |
| Match rate | 100,0% | **100,00%** |

---

## Ambiente Computacional

**Sistema operacional:** Linux · Python 3.11 · Conda (`iam`)

### Bibliotecas e versões

| Categoria | Biblioteca | Versão | Uso principal |
|-----------|-----------|--------|---------------|
| Coleta | `ftplib` (stdlib) | — | Download FTP do DATASUS |
| Conversão | `datasus-dbc` | 0.1.3 | Descompressão `.dbc` |
| Conversão | `dbfread` | 2.0.7 | Leitura `.dbf` |
| Conversão | `pyreaddbc` | 1.2.0 | Leitura alternativa `.dbc` |
| Manipulação | `pandas` | 3.0.2 | ETL, pivot, merge, filtros |
| Manipulação | `numpy` | 2.4.4 | Operações numéricas |
| Paralelismo | `concurrent.futures` (stdlib) | — | Tradução em multiprocessamento |
| Visualização | `matplotlib` | 3.10.8 | Gráficos base |
| Visualização | `seaborn` | 0.13.2 | Estilização estatística |
| Machine Learning | `scikit-learn` | 1.8.0 | Pipeline, métricas, split |
| Machine Learning | `xgboost` | 3.2.0 | Classificador XGBoost |
| Machine Learning | `lightgbm` | 4.6.0 | Classificador LightGBM |
| Interpretabilidade | `shap` | 0.52.0 | SHAP TreeExplainer |
| Sobrevivência | `lifelines` | 0.30.3 | KaplanMeierFitter, CoxPHFitter, logrank_test |
| Versionamento | `git` | — | Controle de versão |

---

## Problemas Encontrados e Soluções Aplicadas

| # | Problema | Causa | Solução |
|---|----------|-------|---------|
| 1 | Parser `.cnv` com token extra | Formato TabWin inclui código interno no final de cada linha | Descarte do último token ao montar a descrição |
| 2 | Marcador `L` ignorado nos `.def` | Parser reconhecia apenas `X`, `S`, `C` | Inclusão de `L` na lista de marcadores válidos |
| 3 | Colunas `_DESC` vazias no EQ | Tabela de equipamentos não tem mapeamento `.cnv` | Comportamento esperado; documentado |
| 4 | OOM ao carregar todo o CNES | 120k+ hospitais × 11 anos × 5 tabelas | Filtro "hospitais VIP" — carrega apenas os 506 que aparecem no SIH-IAM |
| 5 | Data leakage temporal no merge | Merge anterior usava só `codigo_cnes`, associando snapshot único (Dez/2025) | Chave dupla `codigo_cnes` + `competencia` — foto mensal exata do hospital |
| 6 | `FutureWarning` no `fillna` | Pandas 3.x deprecou downcasting silencioso | Documentado; usar `.infer_objects(copy=False)` nas próximas versões |
| 7 | CNES sem limpeza de nulos | Critério de 70% só aplicado ao SIH | Extensão da limpeza ao CNES após merge (−35 colunas) |
| 8 | RF não suporta NaN | `RandomForestClassifier` lança exceção com valores ausentes | `SimpleImputer(strategy='median')` antes do fit |
| 9 | Falha na tradução de Raça/Cor e UTI | Dicionários `.cnv` usam *zero-padding* (ex: `01`) mas os dados originais são numéricos (`1`). | Refatoração do `information_translation.py` para injetar as duas versões da chave (com e sem zeros) no dicionário Python. |
| 10 | `ValueError` em categorias traduzidas | O EDA (Notebook 04) tentava aplicar lógicas usando `.astype(int)` em colunas que já haviam sido transformadas em *strings* (`Público`). | Migração da lógica estrutural (ex: agrupamento `natureza_juridica`) para o ETL (Notebook 02), isolando o EDA apenas para consumo. |
| 11 | *Data Leakage* com Split Temporal | O Notebook 05 deletava o `ano_competencia` como *leakage*, o que impedia o Notebook 06 de dividir Treino (2015-2022) e Teste (2023+). | O Notebook 05 foi atualizado para preservar as datas puras. A eliminação das variáveis de data (`competencia`, `ano_competencia`, `data_internacao`) agora é feita **cirurgicamente no Notebook 06**, após o split e instantes antes da injeção no ML. |
| 12 | Coluna `uti_mes_total` renomeada | O Dicionário SIH preservou o sufixo numérico `_cod`, gerando `uti_mes_total_cod`, o que causou falha no Notebook 07 (Cox). | Adição de leitura flexível `df.get('uti_mes_total', df.get('uti_mes_total_cod'))`. |
| 13 | Máscaras Vazias no Kaplan-Meier | O Notebook 07 mantinha lógicas binárias (`sexo == 1`), gerando séries vazias nas strings. | Substituição por lógicas em texto (`sexo == 'Masculino'`). |
| 14 | Orquestração Lenta | Rodar tudo manualmente exigia esperar *downloads* demorados a cada pequena modificação no ML. | Desenvolvimento de `run_pipeline.py`, um orquestrador programático idempotente que interliga os Notebooks e permite comentar as etapas 01a e 01b. |

---

*Última atualização: 01/09/2026*
