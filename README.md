# Predição de Letalidade Hospitalar por IAM no SUS

> TCC — MBA em Data Science e Analytics  
> Integração de dados SIH/DATASUS e CNES com Machine Learning e Análise de Sobrevivência

---

## Sumário

- [Contexto](#contexto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Reproduzir](#como-reproduzir)
- [Pipeline](#pipeline)
- [Fontes de Dados](#fontes-de-dados)
- [Stack Tecnológico](#stack-tecnológico)

---

## Contexto

O Infarto Agudo do Miocárdio (IAM) é uma das principais causas de mortalidade hospitalar no Brasil. Este projeto aplica técnicas de Machine Learning e Análise de Sobrevivência sobre dados públicos do DATASUS para modelar o risco de óbito hospitalar em internações por IAM (CID-10: I21) no SUS.

A base integra registros de internação (SIH/AIH) com dados estruturais dos hospitais (CNES), investigando o impacto conjunto de fatores clínicos, sociodemográficos e de infraestrutura hospitalar no desfecho do paciente.

---

## Estrutura do Projeto

```
TCC/
│
├── data/
│   ├── raw/            # Dados brutos extraídos via FTP do DATASUS — NUNCA modificados
│   ├── input/          # Dados transformados de .dbc para .csv
│   ├── interim/        # Dados intermediários (limpeza, merge SIH+CNES)
│   ├── processed/      # Base final pronta para modelagem
│   └── external/       # Dicionários, metadados CNES, tabelas CID-10 (.def/.cnv)
│
├── notebooks/
│   ├── 01_data_collection.ipynb              # Download FTP + conversão DBC→CSV
│   ├── 02_etl_database_integration.ipynb     # Limpeza, filtro IAM, merge SIH+CNES
│   ├── 03_feature_selection.ipynb            # Seleção de variáveis
│   ├── 04_analysis_exploration_visualization.ipynb  # EDA e visualizações
│   ├── 05_predictive_modeling.ipynb          # Regressão Logística, RF, XGBoost, LightGBM
│   └── 06_survival_analysis.ipynb            # Kaplan-Meier, Regressão de Cox
│
├── src/
│   └── utils/
│       ├── download_data_from_datasus.py     # Download via FTP do DATASUS
│       ├── converter_dbc_para_csv.py         # Conversão .dbc → .csv (Windows e Linux/macOS)
│       └── information_translation.py        # Tradução de códigos via .def/.cnv
│
├── reports/
│   ├── figures/        # Gráficos e visualizações exportados
│   └── results/        # Métricas, tabelas e outputs dos modelos
│
├── requirements.txt    # Dependências com versões fixas
└── .gitignore
```

> **Nota:** A pasta `data/` não é versionada no git. Os dados são gerados localmente ao rodar o pipeline (ver [Como Reproduzir](#como-reproduzir)).

---

## Como Reproduzir

### Pré-requisitos

- Python >= 3.11

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/<seu-usuario>/iam-sus-mortality.git
cd iam-sus-mortality

# 2. Crie o ambiente virtual
python -m venv .venv

# 3. Ative o ambiente virtual
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute os notebooks em ordem
jupyter notebook
```

### Ordem de execução dos notebooks

| # | Notebook | O que faz |
|---|---|---|
| 01 | `01_data_collection.ipynb` | Download dos `.dbc` do FTP + conversão para `.csv` |
| 02 | `02_etl_database_integration.ipynb` | Limpeza, filtro CID I21, merge SIH+CNES |
| 03 | `03_feature_selection.ipynb` | Seleção das variáveis para modelagem |
| 04 | `04_analysis_exploration_visualization.ipynb` | EDA e visualizações |
| 05 | `05_predictive_modeling.ipynb` | Treino, tuning e comparação de modelos ML |
| 06 | `06_survival_analysis.ipynb` | Kaplan-Meier e regressão de Cox |

---

## Pipeline

```
DATASUS (SIH + CNES)
        │
        ▼
  data/raw/              ← extração bruta, sem modificação
        │
        ▼
  data/input/            ← conversão .dbc → .csv
        │
        ▼
  data/interim/          ← limpeza, merge SIH+CNES, filtro CID I21
        │
        ▼
  data/processed/        ← feature engineering, encoding, split treino/teste
        │
        ▼
  Modelagem ML           ← Regressão Logística, Random Forest, XGBoost, LightGBM
        │
        ▼
  Análise de Sobrevivência ← Kaplan-Meier, Regressão de Cox
        │
        ▼
  reports/               ← métricas, SHAP, figuras, tabelas
```

---

## Fontes de Dados

| Base | Descrição | Acesso |
|------|-----------|--------|
| SIH/DATASUS | Autorizações de Internação Hospitalar (AIH) com CID-10 I21 | FTP DATASUS |
| CNES | Cadastro Nacional de Estabelecimentos de Saúde | FTP DATASUS |

Os dados são extraídos via FTP pelo script `src/utils/download_data_from_datasus.py`, acionado no notebook `01_data_collection.ipynb`. Não é necessário baixar arquivos manualmente.

---

## Stack Tecnológico

| Categoria | Bibliotecas |
|-----------|-------------|
| Coleta de dados | `ftplib` (stdlib), `datasus-dbc`, `dbfread` |
| Manipulação | `pandas`, `numpy` |
| Visualização | `matplotlib`, `seaborn`, `plotly` |
| Machine Learning | `scikit-learn`, `xgboost`, `lightgbm` |
| Análise de Sobrevivência | `lifelines` |
| Interpretabilidade | `shap` |
| Notebooks | `jupyter`, `nbconvert` |
| Qualidade de código | `black`, `flake8` |

---

## Período e Escopo

- **Período:** 2019–2025 (configurável no notebook 01)
- **CID-10:** I21 (Infarto Agudo do Miocárdio)
- **Âmbito:** internações no SUS (rede pública)

---

*Projeto desenvolvido como TCC do MBA em Data Science e Analytics.*
