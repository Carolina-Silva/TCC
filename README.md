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
iam-sus-mortality/
│
├── data/
│   ├── raw/            # Dados brutos extraídos via FTP do DATASUS — NUNCA modificados
│   ├── input/          # Dados transformados de .dbc para .csv 
│   ├── interim/        # Dados intermediários (limpeza, merge SIH+CNES)
│   ├── processed/      # Base final pronta para modelagem
│   └── external/       # Dicionários, metadados CNES, tabelas CID-10
│
├── notebooks/
│   ├── 01_coleta_dados.ipynb         # Extração, inspeção inicial
│   ├── 02_eda.ipynb                  # Análise exploratória e visualizações
│   ├── 03_feature_engineering.ipynb  # Merge SIH+CNES, criação de variáveis
│   ├── 04_modelagem.ipynb            # Treino, tuning e comparação de modelos
│   └── 05_analise_sobrevivencia.ipynb # Kaplan-Meier, regressão de Cox
│
├── src/
│   ├── converter_dbc_para_csv.py         # Função criada para converção de tipo .dbc para .csv
│   ├── donwload_data_from_datasus.py     # Função de download FTP dos dados puros do DATASUS
│   └── utils.py            # Helpers, constantes, logging
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

# 2. Crie o ambiente virtual e instale as dependências


# 3. Ative o ambiente virtual
   # Linux/macOS
   # Windows

# 4. Execute o pipeline completo

```

### Comandos disponíveis

```

```

---

## Pipeline

```
DATASUS (SIH + CNES)
        │
        ▼
  data/raw/              ← extração bruta, sem modificação
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
| SIH/DATASUS | Autorizações de Internação Hospitalar (AIH) com CID-10 I21 | via `pysus` |
| CNES | Cadastro Nacional de Estabelecimentos de Saúde | via `pysus` |

Os dados são extraídos programaticamente pela biblioteca [pysus](https://github.com/AlertaDengue/PySUS). Não é necessário baixar arquivos manualmente — o script `src/data_collection.py` (acionado por `make collect`) faz tudo automaticamente.

---

## Stack Tecnológico

| Categoria | Bibliotecas |
|-----------|-------------|
| Coleta de dados | `pysus` |
| Manipulação | `pandas`, `numpy` |
| Visualização | `matplotlib`, `seaborn`, `plotly` |
| Machine Learning | `scikit-learn`, `xgboost`, `lightgbm` |
| Análise de Sobrevivência | `lifelines` |
| Interpretabilidade | `shap` |
| Notebooks | `jupyter`, `nbconvert` |
| Qualidade de código | `black`, `flake8` |

---

## Período e Escopo

- **Período:** 2019–2023 (ajustável em `src/utils.py`)
- **CID-10:** I21 (Infarto Agudo do Miocárdio)
- **Âmbito:** internações no SUS (rede pública)

---

*Projeto desenvolvido como TCC do MBA em Data Science e Analytics.*
