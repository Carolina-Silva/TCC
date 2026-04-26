import os

import pandas as pd
#import pyreaddbc
from dbfread import DBF
import datasus_dbc


# def converter_dbc_para_csv(caminho_dbc: str, caminho_csv: str) -> None:
#     """Converte um arquivo .dbc do DataSUS diretamente para .csv.

#     O processo intermediário cria um arquivo .dbf temporário na mesma pasta
#     do .csv, que é removido automaticamente ao final (mesmo em caso de erro).

#     Parameters
#     ----------
#     caminho_dbc : str
#         Caminho completo para o arquivo de entrada no formato ``.dbc``.
#     caminho_csv : str
#         Caminho completo para o arquivo de saída no formato ``.csv``.
#         O diretório de destino deve existir antes da chamada.

#     Notes
#     -----
#     - A leitura do .dbf usa a codificação ``iso-8859-1`` (padrão dos sistemas
#       do governo brasileiro).
#     - O CSV de saída é salvo em ``utf-8`` para compatibilidade universal.
#     """
#     # Arquivo .dbf temporário fica ao lado do .csv de destino
#     caminho_dbf = caminho_csv.replace(".csv", ".dbf")

#     try:
#         pyreaddbc.dbc2dbf(caminho_dbc, caminho_dbf)

#         tabela = DBF(caminho_dbf, encoding="iso-8859-1")
#         df = pd.DataFrame(iter(tabela))

#         df.to_csv(caminho_csv, index=False, encoding="utf-8")

#     finally:
#         if os.path.exists(caminho_dbf):
#             os.remove(caminho_dbf)



def converter_dbc_para_csv_win(caminho_dbc: str, caminho_csv: str) -> None:
    """
    Converte um arquivo .dbc do DataSUS para .csv no Windows.
    """
    # Arquivo .dbf temporário
    caminho_dbf = caminho_csv.replace(".csv", ".dbf")

    try:
        # No Windows, usamos o datasus_dbc.decompress no lugar do dbc2dbf
        datasus_dbc.decompress(caminho_dbc, caminho_dbf)

        # Leitura do DBF (mantendo sua lógica original)
        tabela = DBF(caminho_dbf, encoding="iso-8859-1")
        df = pd.DataFrame(iter(tabela))

        # Salva como CSV em UTF-8
        df.to_csv(caminho_csv, index=False, encoding="utf-8")

    except Exception as e:
        print(f"Erro na conversão: {e}")
        
    finally:
        # Garante a limpeza do arquivo temporário
        if os.path.exists(caminho_dbf):
            os.remove(caminho_dbf)


def converter_dbc_para_csv_lote(pasta_origem: str, pasta_destino: str) -> None:
    """Converte em lote todos os arquivos .dbc de uma pasta para .csv.

    Itera sobre todos os arquivos .dbc encontrados em pasta_origem e
    salva os CSVs correspondentes em pasta_destino 

    Parameters
    ----------
    pasta_origem : str
        Diretório contendo os arquivos .dbc a converter.
    pasta_destino : str
        Diretório onde os arquivos .csv serão salvos.
        Criado automaticamente se não existir.

    Examples
    --------
    >>> processar_lote_dbc("data/raw/SIH", "data/input/SIH")
    Processando: RDSP2501.dbc
    Concluído: rdsp2501.csv
    ...
    """
    os.makedirs(pasta_destino, exist_ok=True)

    for arquivo in os.listdir(pasta_origem):
        if not arquivo.lower().endswith(".dbc"):
            continue

        caminho_dbc = os.path.join(pasta_origem, arquivo)
        nome_csv = arquivo.lower().replace(".dbc", ".csv")
        caminho_csv = os.path.join(pasta_destino, nome_csv)

        print(f"Processando: {arquivo}")
        converter_dbc_para_csv_win(caminho_dbc, caminho_csv)
        print(f"Concluído: {nome_csv}")
