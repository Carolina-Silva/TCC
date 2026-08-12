import os
import platform
import struct

import pandas as pd
import datasus_dbc

try:
    import pyreaddbc
    _PYREADDBC_AVAILABLE = True
except ImportError:
    _PYREADDBC_AVAILABLE = False


# ---------------------------------------------------------------------------
# Leitor de DBF robusto (substitui dbfread)
# ---------------------------------------------------------------------------
# O dbfread falha em arquivos CNES do DATASUS que usam 0x00 como terminador
# do bloco de field descriptors em vez do padrão 0x0D. Este leitor aceita
# ambos os terminadores e lida com encodings do governo brasileiro.

def _ler_dbf(caminho_dbf: str, encoding: str = "iso-8859-1") -> pd.DataFrame:
    """Lê um arquivo .dbf e retorna um DataFrame.

    Implementação própria que aceita tanto 0x0D quanto 0x00 como terminador
    do bloco de field descriptors — necessário para arquivos CNES do DATASUS.

    Parameters
    ----------
    caminho_dbf : str
        Caminho para o arquivo .dbf.
    encoding : str
        Encoding das strings. Padrão: ``iso-8859-1`` (Latin-1, padrão DATASUS).

    Returns
    -------
    pd.DataFrame
        DataFrame com os registros do arquivo.
    """
    with open(caminho_dbf, "rb") as f:
        raw_header = f.read(32)

    if len(raw_header) < 32:
        raise ValueError(
            f"Arquivo DBF inválido ou truncado: cabeçalho tem apenas "
            f"{len(raw_header)} bytes (esperado: 32)."
        )

    num_records  = struct.unpack_from("<I", raw_header, 4)[0]
    header_size  = struct.unpack_from("<H", raw_header, 8)[0]
    record_size  = struct.unpack_from("<H", raw_header, 10)[0]

    # ── Leitura dos field descriptors ────────────────────────────────────────
    field_names  = []
    field_types  = []
    field_lengths = []

    with open(caminho_dbf, "rb") as f:
        f.seek(32)  # pula cabeçalho principal

        while f.tell() < header_size - 1:
            descriptor = f.read(32)
            if len(descriptor) < 1:
                break
            # Terminadores válidos: 0x0D (padrão dBASE) ou 0x00 (DATASUS/FoxPro)
            if descriptor[0] in (0x0D, 0x00):
                break
            if len(descriptor) < 32:
                break

            name  = descriptor[0:11].split(b"\x00")[0].decode(encoding, errors="replace").strip()
            ftype = chr(descriptor[11])
            flen  = descriptor[16]

            field_names.append(name)
            field_types.append(ftype)
            field_lengths.append(flen)

    if not field_names:
        raise ValueError("Nenhum field descriptor encontrado no arquivo DBF.")

    # ── Leitura dos registros ────────────────────────────────────────────────
    # Formato de cada registro: 1 byte de flag de deleção + campos
    rows = []
    with open(caminho_dbf, "rb") as f:
        f.seek(header_size)  # pula cabeçalho completo

        for _ in range(num_records):
            raw_record = f.read(record_size)
            if len(raw_record) < record_size:
                break  # arquivo truncado — para sem quebrar

            deletion_flag = raw_record[0:1]
            if deletion_flag == b"*":
                continue  # registro marcado como deletado — ignora

            row = {}
            pos = 1  # pula flag de deleção
            for name, ftype, flen in zip(field_names, field_types, field_lengths):
                raw_val = raw_record[pos: pos + flen]
                val_str = raw_val.decode(encoding, errors="replace").strip()

                if ftype in ("N", "F"):
                    try:
                        row[name] = float(val_str) if "." in val_str else int(val_str)
                    except (ValueError, TypeError):
                        row[name] = None
                elif ftype == "L":
                    row[name] = val_str.upper() in ("T", "Y", "1")
                else:
                    row[name] = val_str

                pos += flen

            rows.append(row)

    return pd.DataFrame(rows, columns=field_names)


# ---------------------------------------------------------------------------
# Funções públicas
# ---------------------------------------------------------------------------

def converter_dbc_para_csv(caminho_dbc: str, caminho_csv: str) -> None:
    """Converte um arquivo .dbc do DataSUS para .csv.

    Seleciona automaticamente a implementação correta de acordo com o sistema
    operacional:

    - **Windows**: usa ``datasus_dbc.decompress`` para descompressão.
    - **Linux / macOS**: usa ``pyreaddbc.dbc2dbf`` (requer ``pyreaddbc``).

    A leitura do ``.dbf`` intermediário usa um leitor próprio que aceita tanto
    ``0x0D`` quanto ``0x00`` como terminador de field descriptors — necessário
    para arquivos CNES do DATASUS que divergem do padrão dBASE III.

    Parameters
    ----------
    caminho_dbc : str
        Caminho completo para o arquivo de entrada no formato ``.dbc``.
    caminho_csv : str
        Caminho completo para o arquivo de saída no formato ``.csv``.
        O diretório de destino deve existir antes da chamada.

    Raises
    ------
    RuntimeError
        Se o sistema não for Windows e ``pyreaddbc`` não estiver instalado.
    Exception
        Propaga qualquer erro ocorrido durante a descompressão ou leitura do DBF.

    Notes
    -----
    - A leitura do .dbf usa a codificação ``iso-8859-1`` (padrão dos sistemas
      do governo brasileiro).
    - O CSV de saída é salvo em ``utf-8`` para compatibilidade universal.
    """
    caminho_dbf = caminho_csv.replace(".csv", ".dbf")

    try:
        # 1) Descompressão: .dbc → .dbf
        if platform.system() == "Windows":
            datasus_dbc.decompress(caminho_dbc, caminho_dbf)
        else:
            if not _PYREADDBC_AVAILABLE:
                raise RuntimeError(
                    "pyreaddbc não está instalado. "
                    "Execute: pip install pyreaddbc"
                )
            pyreaddbc.dbc2dbf(caminho_dbc, caminho_dbf)

        # 2) Verificação mínima do arquivo gerado
        tamanho_dbf = os.path.getsize(caminho_dbf)
        if tamanho_dbf < 32:
            raise ValueError(
                f"Descompressão produziu um arquivo inválido "
                f"({tamanho_dbf} bytes). O .dbc pode estar corrompido."
            )

        # 3) Leitura do .dbf com leitor robusto
        df = _ler_dbf(caminho_dbf, encoding="iso-8859-1")

        # 4) Exportação para CSV em UTF-8
        df.to_csv(caminho_csv, index=False, encoding="utf-8")

    except Exception as e:
        print(f"Erro na conversão de '{caminho_dbc}': {e}")
        raise

    finally:
        if os.path.exists(caminho_dbf):
            os.remove(caminho_dbf)


def converter_dbc_para_csv_lote(pasta_origem: str, pasta_destino: str) -> None:
    """Converte em lote todos os arquivos .dbc de uma pasta para .csv.

    Itera sobre todos os arquivos .dbc encontrados em ``pasta_origem`` e
    salva os CSVs correspondentes em ``pasta_destino``.

    Parameters
    ----------
    pasta_origem : str
        Diretório contendo os arquivos .dbc a converter.
    pasta_destino : str
        Diretório onde os arquivos .csv serão salvos.
        Criado automaticamente se não existir.

    Examples
    --------
    >>> converter_dbc_para_csv_lote("data/raw/SIH", "data/input/SIH")
    Processando: RDSP2501.dbc
    Concluído: rdsp2501.csv
    ...
    """
    os.makedirs(pasta_destino, exist_ok=True)

    erros = []
    for arquivo in os.listdir(pasta_origem):
        if not arquivo.lower().endswith(".dbc"):
            continue

        caminho_dbc = os.path.join(pasta_origem, arquivo)
        nome_csv = arquivo.lower().replace(".dbc", ".csv")
        caminho_csv = os.path.join(pasta_destino, nome_csv)

        print(f"Processando: {arquivo}")
        try:
            converter_dbc_para_csv(caminho_dbc, caminho_csv)
            print(f"Concluído: {nome_csv}")
        except Exception as e:
            print(f"  ↳ Falha ignorada, continuando lote: {e}")
            erros.append(arquivo)

    if erros:
        print(f"\nConversão concluída com {len(erros)} erro(s):")
        for e in erros:
            print(f"  - {e}")
    else:
        print("\nTodos os arquivos convertidos com sucesso.")
