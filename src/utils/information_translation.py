import os
import pandas as pd

def mapear_colunas_def(caminho_def: str) -> dict[str, str]:
    mapa_coluna_cnv = {}

    if not os.path.exists(caminho_def):
        print(f"Aviso: Arquivo .def não encontrado em {caminho_def}")
        return mapa_coluna_cnv

    with open(caminho_def, "r", encoding="latin-1") as f:
        for linha in f:
            linha = linha.strip()

            # Pula linhas em branco ou comentários desativados do TabWin
            if not linha or linha.startswith(";"):
                continue

            # Registros válidos no TabWin começam com marcadores de tipo (normalmente X, S, C)
            # L = Lista, X = eXibir, S = Soma, C = Contagem — todos referenciam CNVs
            if linha[0].upper() in ["X", "S", "C", "L"]:
                partes = [p.strip() for p in linha.split(",")]

                # Precisamos de pelo menos o identificador/nome e o caminho do arquivo
                if len(partes) >= 2:
                    nome_coluna = partes[1].upper()

                    # O arquivo CNV geralmente fica na última posição da linha
                    ultima_parte = partes[-1]

                    if "CNV\\" in ultima_parte.upper():
                        # Extrai apenas o nome do arquivo .cnv de dentro do caminho (ex: CNV\COMPT.CNV -> COMPT.CNV)
                        nome_cnv = ultima_parte.split("\\")[-1].strip()

                        if nome_cnv:
                            mapa_coluna_cnv[nome_coluna] = nome_cnv

    return mapa_coluna_cnv


def carregar_dicionario_cnv(caminho_cnv: str) -> dict[str, str]:
    de_para = {}
    if not os.path.exists(caminho_cnv):
        return de_para

    with open(caminho_cnv, "r", encoding="latin-1") as f:
        linhas = f.readlines()

    for linha in linhas:
        linha = linha.strip()
        if (
            not linha
            or linha.startswith(";")
            or linha.upper().startswith("VALOR")
        ):
            continue

        partes = linha.split()

        # Formato do arquivo .cnv (largura fixa do TabWin):
        #   CÓDIGO  DESCRIÇÃO [PALAVRAS...]  CODIGO_TABWIN
        # O primeiro token é o código; o último token é o código interno do
        # TabWin (ex: "1", "D", "-Z") e deve ser descartado.
        # Tudo que está no meio é a descrição legível.
        if len(partes) >= 3:
            codigo = partes[0].strip()
            # Remove o último token (código TabWin) e junta o restante
            descricao = " ".join(partes[1:-1]).strip()
            de_para[codigo] = descricao
        elif len(partes) == 2:
            # Linha sem código TabWin: código + descrição diretamente
            codigo, descricao = partes
            de_para[codigo.strip()] = descricao.strip()

    return de_para


def traduzir_csv_datasus(
    caminho_csv: str,
    mapa_diretrizes: dict[str, str],
    pasta_cnv: str,
    caminho_salvar: str,
) -> None:
    df = pd.read_csv(caminho_csv)

    for coluna_csv in df.columns:
        coluna_normalizada = coluna_csv.upper()

        if coluna_normalizada in mapa_diretrizes:
            arquivo_cnv = mapa_diretrizes[coluna_normalizada]

            # O DATASUS às vezes diferencia maiúsculas/minúsculas nos nomes dos arquivos físicos
            caminho_completo_cnv = os.path.join(pasta_cnv, arquivo_cnv)
            if not os.path.exists(caminho_completo_cnv):
                caminho_completo_cnv = os.path.join(
                    pasta_cnv, arquivo_cnv.lower()
                )
            if not os.path.exists(caminho_completo_cnv):
                caminho_completo_cnv = os.path.join(
                    pasta_cnv, arquivo_cnv.upper()
                )

            if os.path.exists(caminho_completo_cnv):
                print(
                    f"Traduzindo a coluna '{coluna_csv}' com o dicionário '{arquivo_cnv}'..."
                )
                dicionario_traducao = carregar_dicionario_cnv(
                    caminho_completo_cnv
                )

                df[coluna_csv] = df[coluna_csv].astype(str).str.strip()

                nova_coluna_desc = f"{coluna_csv}_DESC"
                df[nova_coluna_desc] = df[coluna_csv].map(dicionario_traducao)

    df.to_csv(caminho_salvar, index=False)
    print(f"\nSucesso! O arquivo traduzido foi salvo em: {caminho_salvar}")