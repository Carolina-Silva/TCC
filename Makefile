# =============================================================================
# TCC - Predição de Letalidade Hospitalar por IAM no SUS
# =============================================================================
# Uso:
#   make help        → lista todos os comandos disponíveis
#   make setup       → instala dependências e prepara o ambiente
#   make all         → executa o pipeline completo do zero
#
# Requisitos: Python >= 3.10, pip

PYTHON     = python3
PIP        = pip3
VENV       = .venv
VENV_PY    = $(VENV)/bin/python
VENV_PIP   = $(VENV)/bin/pip
NOTEBOOKS  = notebooks

# Detecta se o venv já está ativo; se não, usa o venv local
ifeq ($(VIRTUAL_ENV),)
    RUN = $(VENV)/bin
else
    RUN = $(shell dirname $(shell which python))
endif

.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Utilitários
# -----------------------------------------------------------------------------

.PHONY: help
help:  ## Mostra esta mensagem de ajuda
	@echo ""
	@echo "  TCC — Predição de Letalidade por IAM no SUS"
	@echo "  ============================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}'
	@echo ""

# -----------------------------------------------------------------------------
# Ambiente
# -----------------------------------------------------------------------------

.PHONY: venv
venv: ## Cria o ambiente virtual Python
	@echo "→ Criando ambiente virtual em $(VENV)/"
	$(PYTHON) -m venv $(VENV)
	@echo "  Ative com: source $(VENV)/bin/activate"

.PHONY: install
install: ## Instala as dependências do requirements.txt
	@echo "→ Instalando dependências..."
	$(RUN)/pip install --upgrade pip
	$(RUN)/pip install -r requirements.txt
	@echo "✓ Dependências instaladas."

.PHONY: setup
setup: venv install ## Cria venv + instala dependências (primeiro uso)
	@echo "✓ Ambiente pronto. Rode: source $(VENV)/bin/activate"

# -----------------------------------------------------------------------------
# Estrutura de pastas
# -----------------------------------------------------------------------------

.PHONY: dirs
dirs: ## Cria toda a estrutura de pastas do projeto
	@echo "→ Criando estrutura de diretórios..."
	mkdir -p data/raw data/interim data/processed data/external
	mkdir -p reports/figures reports/results
	mkdir -p src
	touch data/raw/.gitkeep
	touch data/interim/.gitkeep
	touch data/processed/.gitkeep
	touch data/external/.gitkeep
	touch reports/figures/.gitkeep
	touch reports/results/.gitkeep
	@echo "✓ Estrutura criada."

# -----------------------------------------------------------------------------
# Pipeline de dados
# -----------------------------------------------------------------------------

.PHONY: collect
collect: ## [1/4] Coleta dados do DATASUS via pysus → data/raw/
	@echo "→ Coletando dados SIH e CNES..."
	$(RUN)/python src/data_collection.py
	@echo "✓ Dados salvos em data/raw/"

.PHONY: preprocess
preprocess: ## [2/4] Limpeza, merge SIH+CNES → data/interim/ e data/processed/
	@echo "→ Pré-processando e integrando bases..."
	$(RUN)/python src/preprocessing.py
	@echo "✓ Base processada em data/processed/"

.PHONY: train
train: ## [3/4] Treina e avalia os modelos de ML
	@echo "→ Treinando modelos..."
	$(RUN)/python src/models.py
	@echo "✓ Resultados em reports/results/"

.PHONY: evaluate
evaluate: ## [4/4] Gera métricas finais, SHAP e figuras
	@echo "→ Gerando avaliações e figuras..."
	$(RUN)/python src/evaluate.py
	@echo "✓ Figuras em reports/figures/"

.PHONY: pipeline
pipeline: collect preprocess train evaluate ## Roda o pipeline completo (etapas 1→4)
	@echo ""
	@echo "✓ Pipeline concluído com sucesso."

# -----------------------------------------------------------------------------
# Notebooks
# -----------------------------------------------------------------------------

.PHONY: notebooks
notebooks: ## Executa todos os notebooks em ordem (gera outputs)
	@echo "→ Executando notebooks..."
	$(RUN)/jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=3600 \
		--inplace $(NOTEBOOKS)/01_coleta_dados.ipynb
	$(RUN)/jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=3600 \
		--inplace $(NOTEBOOKS)/02_eda.ipynb
	$(RUN)/jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=3600 \
		--inplace $(NOTEBOOKS)/03_feature_engineering.ipynb
	$(RUN)/jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=3600 \
		--inplace $(NOTEBOOKS)/04_modelagem.ipynb
	$(RUN)/jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=3600 \
		--inplace $(NOTEBOOKS)/05_analise_sobrevivencia.ipynb
	@echo "✓ Notebooks executados."

.PHONY: lab
lab: ## Abre o Jupyter Lab no navegador
	$(RUN)/jupyter lab

# -----------------------------------------------------------------------------
# Reprodutibilidade total
# -----------------------------------------------------------------------------

.PHONY: all
all: dirs pipeline notebooks ## Roda tudo do zero (setup já feito)
	@echo ""
	@echo "  ✓ Projeto executado com sucesso."
	@echo "  → Resultados: reports/results/"
	@echo "  → Figuras:    reports/figures/"
	@echo ""

# -----------------------------------------------------------------------------
# Qualidade de código
# -----------------------------------------------------------------------------

.PHONY: lint
lint: ## Verifica estilo do código (flake8 + black)
	@echo "→ Checando estilo..."
	$(RUN)/flake8 src/ --max-line-length=100
	$(RUN)/black src/ --check --line-length=100
	@echo "✓ Código OK."

.PHONY: format
format: ## Formata automaticamente o código com black
	$(RUN)/black src/ --line-length=100

# -----------------------------------------------------------------------------
# Limpeza
# -----------------------------------------------------------------------------

.PHONY: clean-interim
clean-interim: ## Remove dados intermediários (mantém raw e processed)
	@echo "→ Limpando data/interim/..."
	find data/interim -type f ! -name '.gitkeep' -delete
	@echo "✓ Limpo."

.PHONY: clean-outputs
clean-outputs: ## Remove outputs de notebooks e relatórios gerados
	find reports -type f ! -name '.gitkeep' -delete
	@echo "✓ Reports limpos."

.PHONY: clean-pyc
clean-pyc: ## Remove arquivos .pyc e caches Python
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null; true

.PHONY: clean
clean: clean-pyc clean-outputs ## Limpeza geral (mantém dados e venv)

.PHONY: clean-all
clean-all: clean clean-interim ## Limpeza completa (mantém só raw e venv)
	@echo "→ Para recriar tudo: make all"
