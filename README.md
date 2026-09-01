# Predição de Letalidade Hospitalar por IAM no SUS

> **TCC — MBA em Data Science e Analytics**
> Integração de dados SIH/DATASUS e CNES com Machine Learning e Análise de Sobrevivência

---

## Sumário

- [Contexto](#contexto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pipeline](#pipeline)
- [Dados](#dados)
- [Como Reproduzir](#como-reproduzir)
- [Stack Tecnológico](#stack-tecnológico)
- [Documentação Técnica](#documentação-técnica)

---

## Contexto

O Infarto Agudo do Miocárdio (IAM) é uma das principais causas de mortalidade hospitalar no Brasil. Este projeto aplica técnicas de **Machine Learning** e **Análise de Sobrevivência** sobre dados públicos do DATASUS para modelar o risco de óbito hospitalar em internações por IAM (CID-10: I21) no SUS.

**Escopo:** Estado de São Paulo — 2019 a 2025

A base integra registros de internação (**SIH/AIH**) com dados estruturais dos hospitais (**CNES**), investigando o impacto conjunto de fatores clínicos, sociodemográficos e de infraestrutura hospitalar no desfecho do paciente.

### Resultados-chave do pipeline de dados

| Métrica | Valor |
|---------|-------|
| Internações SIH brutas (SP/2019–2025) | 2.948.801 |
| Internações por IAM (CID I21) | **48.977** (1,66%) |
| Taxa de letalidade hospitalar | **7,17%** |
| Hospitais distintos | 393 |
| Features na base de modelagem | 665 |
| Match rate IAM → CNES | 100,0% |

---

## Estrutura do Projeto

```
TCC/
│
├── data/
│   ├── raw/            # Dados brutos (.dbc) extraídos via FTP — NUNCA modificados
│   │   ├── SIH/        # 12 arquivos .dbc (~230 MB)
│   │   └── CNES/       # 5 arquivos .dbc (~10 MB)
│   ├── input/          # Dados convertidos .dbc → .csv (~1,4 GB)
│   │   ├── SIH/        # 12 CSVs (~1,3 GB)
│   │   └── CNES/       # 5 CSVs (~100 MB)
│   ├── interim/        # Dados intermediários com tradução de códigos (~1,9 GB)
│   │   ├── sih_iam.csv             # SIH filtrado por IAM + limpeza (25,6 MB)
│   │   └── cnes_hospitais.csv      # CNES consolidado — 5 tabelas (213,2 MB)
│   ├── processed/
│   │   └── base_modelagem.csv      # Base final SIH × CNES (122,9 MB, 48.977 × 665)
│   └── external/       # Dicionários TabWin (.def/.cnv) e metadados CNES
│
├── notebooks/
│   ├── 01a_data_collection.ipynb             # Download FTP + conversão DBC→CSV
│   ├── 01b_data_translation.ipynb            # Tradução de códigos via CNV TabWin
│   ├── 02_etl_ database_integration.ipynb    # Limpeza, filtro IAM, merge SIH+CNES
│   ├── 03_merge_and_eda.ipynb                # Estruturação e análise inicial
│   ├── 04_analysis_exploration_visualization.ipynb  # EDA Profunda e visualizações
│   ├── 05_feature_selection.ipynb            # Seleção de variáveis para modelagem
│   ├── 06_predictive_modeling.ipynb          # Regressão Logística, RF, XGBoost, LightGBM
│   └── 07_survival_analysis.ipynb            # Kaplan-Meier, Regressão de Cox
│
├── run_pipeline.py                           # Orquestrador automatizado para rodar todos os notebooks
├── pipeline_run.log                          # Log de execução gerado automaticamente
│
├── src/
│   └── utils/
│       ├── download_data_from_datasus.py     # Download via FTP do DATASUS (SIH, CNES, SIM)
│       ├── converter_dbc_para_csv.py         # Conversão .dbc → .csv
│       └── information_translation.py        # Tradução de códigos via .def/.cnv (TabWin)
│
├── reports/
│   ├── figures/                              # Gráficos exportados pelo EDA
│   └── pipeline_dados_relatorio.md           # Relatório técnico detalhado do pipeline
│
├── requirements.txt    # Dependências com versões fixas
└── .gitignore
```

> **Nota:** A pasta `data/` não é versionada no git. Os dados são gerados localmente ao executar os notebooks em sequência (ver [Como Reproduzir](#como-reproduzir)).

---

## Pipeline

```
DATASUS FTP (ftp.datasus.gov.br)
        │
        ▼
[1] Coleta (01a)          → data/raw/ e data/input/ (.dbc e .csv brutos)
        │
        ▼
[2] Tradução (01b)        → data/interim/           (códigos convertidos via TabWin)
        │
        ▼
[3] ETL & Merge (02, 03)  → data/interim/           (limpeza, filtros, merge SIH+CNES)
        │
        ▼
[4] EDA (04)              → reports/figures/        (distribuição, correlação, testes estatísticos)
        │
        ▼
[5] Feature Select (05)   → data/processed/         (redução de dimensionalidade, data leakage)
        │
        ▼
[6] Modelagem ML (06)     → Validação Cruzada, XGBoost, Random Forest, SHAP values
        │
        ▼
[7] Sobrevivência (07)    → Kaplan-Meier, Regressão de Cox, Teste Log-Rank
        │
        ▼
reports/            → métricas, SHAP, tabelas de resultados
```

### Funil de registros SIH

```
Internações SIH brutas (SP/2019–2025)  : 2.948.801  (100,0%)
    └─ Filtro CID I21 (IAM)       :    48.977  (  1,7%)
         └─ Filtro adultos ≥ 18   :    48.977  (  1,7%)  ← sem perda adicional
              └─ Match CNES       :    48.977  (100,0%)  ← 0 perdas no join
```

---

## Dados

### Fontes

| Base | Descrição | Período | Acesso |
|------|-----------|---------|--------|
| **SIH/DATASUS** | Autorizações de Internação Hospitalar (AIH) — CID-10 I21 | 2019–2025 (SP) | FTP DATASUS |
| **CNES** | Cadastro Nacional de Estabelecimentos de Saúde | Dez/2025 (SP) | FTP DATASUS |

Os dados são extraídos automaticamente via `src/utils/download_data_from_datasus.py`, acionado no notebook `01_data_collection.ipynb`. **Não é necessário baixar arquivos manualmente.**

### Tabelas CNES utilizadas

| Sigla | Descrição | Relevância para IAM |
|-------|-----------|---------------------|
| **ST** | Estabelecimentos (tabela mestre) | Natureza jurídica, tipo de unidade, localização |
| **LT** | Leitos por especialidade | Leitos cirúrgicos, clínicos, complementares (UTI) |
| **EQ** | Equipamentos | Hemodinâmica, tomografia, ressonância |
| **SR** | Serviços Especializados | Cardiologia, hemodinâmica, UTI coronariana |
| **HB** | Habilitações | Certificações de alta complexidade cardiovascular |

### Perfil da base de modelagem

| Variável | Resultado |
|----------|-----------|
| Total de internações | 48.977 |
| Óbitos | 3.511 (7,2%) |
| Altas | 45.466 (92,8%) |
| Sexo Masculino | 31.135 (63,6%) |
| Sexo Feminino | 17.842 (36,4%) |
| Idade média | 63,5 anos |
| Caráter Urgência | 42.983 (87,8%) |

---

## Como Reproduzir

### Pré-requisitos

- Python >= 3.11
- Conda (recomendado) ou virtualenv

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/<seu-usuario>/iam-sus-mortality.git
cd iam-sus-mortality

# 2. Crie e ative o ambiente
conda create -n tcc python=3.11
conda activate tcc

# Ou com venv:
python -m venv .venv && source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate                            # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a pipeline completa automaticamente!
python run_pipeline.py
```
> O orquestrador `run_pipeline.py` executará todos os notebooks em ordem, tratando as conversões, limpezas, geração de bases e plots automaticamente, gerando um arquivo de auditoria `pipeline_run.log`.

### Ordem de execução dos Notebooks

| # | Notebook | O que faz |
|---|----------|-----------|
| 01a | `01a_data_collection.ipynb` | Download dos `.dbc` via FTP + conversão para `.csv` |
| 01b | `01b_data_translation.ipynb` | Tradução de códigos categóricos pelo Dicionário SUS (TabWin) |
| 02 | `02_etl_ database_integration.ipynb` | Limpeza nulos, filtro CID I21, merge estrutural SIH+CNES |
| 03 | `03_merge_and_eda.ipynb` | Análises exploratórias preliminares |
| 04 | `04_analysis_exploration_visualization.ipynb` | EDA profunda e exportação de gráficos para `reports/` |
| 05 | `05_feature_selection.ipynb` | Tratamento de Data Leakage, constante e dimensionalidade |
| 06 | `06_predictive_modeling.ipynb` | Treino (Split Temporal), Validação Cruzada e XGBoost/SHAP |
| 07 | `07_survival_analysis.ipynb` | Modelagem de Sobrevivência (Kaplan-Meier e Regressão de Cox) |

---

## Stack Tecnológico

| Categoria | Bibliotecas / Ferramentas |
|-----------|--------------------------|
| Coleta de dados | `ftplib` (stdlib), `datasus-dbc==0.1.3`, `dbfread==2.0.7`, `pyreaddbc==1.2.0` |
| Manipulação | `pandas==3.0.2`, `numpy==2.4.4` |
| Visualização | `matplotlib`, `seaborn`, `plotly` |
| Machine Learning | `scikit-learn`, `xgboost`, `lightgbm` |
| Análise de Sobrevivência | `lifelines` |
| Interpretabilidade | `shap` |
| Notebooks | `jupyter`, `nbconvert` |
| Versionamento | `git` |

---

## Documentação Técnica

Para detalhes completos sobre cada etapa do pipeline — incluindo decisões de limpeza, problemas encontrados e soluções aplicadas — consulte o relatório técnico:

📄 [`reports/pipeline_dados_relatorio.md`](reports/pipeline_dados_relatorio.md)

---

## Período e Escopo

- **Período SIH:** 2019 a 2025
- **Período CNES:** Dezembro de 2025 (snapshot mais recente do período)
- **CID-10:** I21 — Infarto Agudo do Miocárdio (incluindo subcódigos I21.0 a I21.9)
- **UF:** São Paulo (SP)
- **Âmbito:** Internações pelo SUS (rede pública)

---

*Projeto desenvolvido como TCC do MBA em Data Science e Analytics.*
