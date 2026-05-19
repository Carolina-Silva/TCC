"""
src/patch_add_tempo_internacao.py
────────────────────────────────────────────────────────────────────────────
Patch que relê os CSVs do SIH, extrai as colunas de tempo (DT_INTER,
DT_SAIDA, DIAS_PERM) e faz um join com a base_modelagem existente.

Não refaz todo o ETL — só adiciona o que está faltando.

Execute:
    python src/patch_add_tempo_internacao.py

Inputs:
    data/input/SIH/rdsp25*.csv      (arquivos originais)
    data/processed/base_modelagem.csv

Output:
    data/processed/base_modelagem.csv   (sobrescreve com novas colunas)
    data/processed/base_modelagem.parquet
"""

import pandas as pd
import glob
from pathlib import Path

# ── Configurações ─────────────────────────────────────────────────────────────
RAW_SIH   = Path("data/input/SIH")
PROCESSED = Path("data/processed")
SEP       = ";"          # ajuste se seus CSVs usam vírgula
ENCODING  = "latin-1"

# Coluna de chave única na sua base (AIH ou equivalente)
# Se não tiver N_AIH, use a combinação CNES + DT_INTER como fallback
COL_CHAVE = "N_AIH"

# ── Colunas de tempo a extrair do SIH ─────────────────────────────────────────
COLUNAS_TEMPO = [
    COL_CHAVE,
    "DT_INTER",    # data de internação  (formato YYYYMMDD no SIH)
    "DT_SAIDA",    # data de saída
    "DIAS_PERM",   # dias de permanência (já calculado pelo DATASUS)
]


def extrair_tempo_sih() -> pd.DataFrame:
    """Lê todos os arquivos SIH e retorna apenas as colunas de tempo."""
    arquivos = sorted(glob.glob(str(RAW_SIH / "*.csv")))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {RAW_SIH}")

    chunks = []
    for arq in arquivos:
        df = pd.read_csv(
            arq, sep=SEP, encoding=ENCODING,
            dtype=str, low_memory=False,
            usecols=lambda c: c in COLUNAS_TEMPO,  # lê só o necessário
        )
        chunks.append(df)
        print(f"  {Path(arq).name}: {len(df):,} linhas")

    tempo = pd.concat(chunks, ignore_index=True)

    # Normaliza chave
    if COL_CHAVE in tempo.columns:
        tempo[COL_CHAVE] = tempo[COL_CHAVE].astype(str).str.strip()

    # Converte datas
    for col in ["DT_INTER", "DT_SAIDA"]:
        if col in tempo.columns:
            tempo[col] = pd.to_datetime(tempo[col], format="%Y%m%d", errors="coerce")

    # Dias de permanência numérico
    if "DIAS_PERM" in tempo.columns:
        tempo["DIAS_PERM"] = pd.to_numeric(tempo["DIAS_PERM"], errors="coerce")

    # Recalcula dias a partir das datas (mais confiável que DIAS_PERM original)
    if "DT_INTER" in tempo.columns and "DT_SAIDA" in tempo.columns:
        tempo["dias_internacao"] = (tempo["DT_SAIDA"] - tempo["DT_INTER"]).dt.days
        # Sanity check
        invalidos = (~tempo["dias_internacao"].between(0, 365)).sum()
        if invalidos > 0:
            print(f"  ⚠️  {invalidos} registros com dias_internacao inválidos → serão NaN")
        tempo.loc[~tempo["dias_internacao"].between(0, 365), "dias_internacao"] = pd.NA

    # Remove duplicatas pela chave (mantém primeira ocorrência)
    if COL_CHAVE in tempo.columns:
        antes = len(tempo)
        tempo = tempo.drop_duplicates(subset=COL_CHAVE, keep="first")
        print(f"\n  Duplicatas removidas: {antes - len(tempo):,}")

    print(f"  Total linhas SIH com tempo: {len(tempo):,}")
    return tempo


def aplicar_patch():
    print("=" * 55)
    print("PATCH — Adicionando colunas de tempo à base_modelagem")
    print("=" * 55)

    # ── Carrega a base atual ───────────────────────────────────────────────────
    arquivo_base = PROCESSED / "base_modelagem.csv"
    if not arquivo_base.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_base}")

    print(f"\n1. Carregando base_modelagem...")
    base = pd.read_csv(arquivo_base, low_memory=False)
    print(f"   Shape original: {base.shape}")

    # Verifica se as colunas já existem
    colunas_ja_existem = [c for c in ["DT_INTER", "DT_SAIDA", "dias_internacao"]
                          if c in base.columns]
    if colunas_ja_existem:
        print(f"   ℹ️  Colunas já existem: {colunas_ja_existem}")
        print("   Sobrescrevendo com valores recalculados...")
        base = base.drop(columns=colunas_ja_existem, errors="ignore")

    # ── Extrai tempo do SIH ────────────────────────────────────────────────────
    print(f"\n2. Extraindo colunas de tempo do SIH...")
    tempo = extrair_tempo_sih()

    # ── Verifica chave ─────────────────────────────────────────────────────────
    if COL_CHAVE not in base.columns:
        print(f"\n  ⚠️  Coluna '{COL_CHAVE}' não encontrada na base_modelagem.")
        print("     Colunas disponíveis:", base.columns.tolist())
        print("\n  Tentando fallback: filtragem por IAM diretamente do SIH...")
        # Fallback: se não há N_AIH, une por índice posicional (menos seguro)
        # Neste caso, recomenda-se refazer o ETL incluindo N_AIH como coluna
        raise ValueError(
            f"Coluna de chave '{COL_CHAVE}' ausente. "
            "Adicione N_AIH ao ETL original e gere novamente a base_modelagem."
        )

    # Normaliza chave na base
    base[COL_CHAVE] = base[COL_CHAVE].astype(str).str.strip()

    # ── Join ───────────────────────────────────────────────────────────────────
    print(f"\n3. Fazendo join por {COL_CHAVE}...")
    colunas_tempo_join = [COL_CHAVE, "DT_INTER", "DT_SAIDA", "dias_internacao"]
    colunas_tempo_join = [c for c in colunas_tempo_join if c in tempo.columns]

    base_com_tempo = base.merge(tempo[colunas_tempo_join], on=COL_CHAVE, how="left")

    # ── Valida cobertura ───────────────────────────────────────────────────────
    sem_data = base_com_tempo["dias_internacao"].isnull().sum() if "dias_internacao" in base_com_tempo.columns else len(base_com_tempo)
    cobertura = 1 - sem_data / len(base_com_tempo)
    print(f"   Registros com dias_internacao preenchido: {cobertura:.1%}")
    if cobertura < 0.90:
        print(f"   ⚠️  Cobertura baixa ({cobertura:.1%}). Verifique se COL_CHAVE está correto.")

    # ── Estatísticas rápidas ───────────────────────────────────────────────────
    if "dias_internacao" in base_com_tempo.columns:
        print(f"\n   Distribuição de dias_internacao:")
        print(f"   {base_com_tempo['dias_internacao'].describe().round(1).to_string()}")

    # ── Salva ──────────────────────────────────────────────────────────────────
    print(f"\n4. Salvando base atualizada...")
    base_com_tempo.to_csv(arquivo_base, index=False)
    base_com_tempo.to_parquet(PROCESSED / "base_modelagem.parquet", index=False)

    print(f"\n✓ base_modelagem atualizada: {base_com_tempo.shape}")
    print(f"  Novas colunas adicionadas: {[c for c in colunas_tempo_join if c != COL_CHAVE]}")
    print(f"\n  Próximo passo: rode o notebook 05_analise_sobrevivencia.ipynb")


if __name__ == "__main__":
    aplicar_patch()
