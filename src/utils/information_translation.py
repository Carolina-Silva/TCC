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
        #   ID_LINHA  DESCRIÇÃO [PALAVRAS...]  CODIGO_TABWIN
        # O último token (CODIGO_TABWIN) é a verdadeira chave de tradução (ex: "1", "2,3", "0-9").
        if len(partes) >= 3:
            codigo_tabwin = partes[-1].strip()
            descricao = " ".join(partes[1:-1]).strip()
            
            # Divide chaves compostas por vírgula (ex: "2,3")
            for c in codigo_tabwin.split(','):
                c = c.strip()
                # Expansão de intervalos numéricos simples (ex: "0-9")
                if '-' in c and len(c.split('-')) == 2:
                    start, end = c.split('-')
                    if start.isdigit() and end.isdigit():
                        for i in range(int(start), int(end) + 1):
                            padded = str(i).zfill(len(start))
                            de_para[padded] = descricao
                            de_para[str(i)] = descricao  # Adiciona versão sem zeros à esquerda
                else:
                    de_para[c] = descricao
                    if c.isdigit():
                        de_para[str(int(c))] = descricao  # Adiciona versão sem zeros à esquerda
                    
        elif len(partes) == 2:
            # Linha simplificada (raro mas possível)
            codigo, descricao = partes
            de_para[codigo.strip()] = descricao.strip()

    return de_para


def traduzir_csv_datasus(
    caminho_csv: str,
    mapa_diretrizes: dict[str, str],
    pasta_cnv: str,
    caminho_salvar: str,
    dicionario_renomeacao: dict = None,
) -> None:
    df = pd.read_csv(caminho_csv, low_memory=False)
    novas_colunas = {}

    for coluna_csv in df.columns:
        coluna_normalizada = coluna_csv.upper()

        # Tratamento especial para datas (formatar para YYYY-MM-DD)
        if 'DT_' in coluna_normalizada or 'DATA' in coluna_normalizada:
            # Tenta tratar strings como '20180101' ou floats como '20180101.0'
            valores_limpos = df[coluna_csv].astype(str).str.replace(r'\.0$', '', regex=True)
            df[coluna_csv] = pd.to_datetime(valores_limpos, format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d').fillna(df[coluna_csv])
            continue  # Pula a tradução de .CNV para colunas de data

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
                dicionario_traducao = carregar_dicionario_cnv(
                    caminho_completo_cnv
                )

                # Mantemos a coluna original como string para garantir o mapeamento
                df[coluna_csv] = df[coluna_csv].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                
                # Adiciona a nova coluna _DESC ao dicionário de novas colunas
                nova_coluna_desc = f"{coluna_csv}_DESC"
                novas_colunas[nova_coluna_desc] = df[coluna_csv].map(dicionario_traducao)

    # Concatena todas as novas colunas de uma vez para evitar DataFrame Fragmentation Warning
    if novas_colunas:
        df = pd.concat([df, pd.DataFrame(novas_colunas)], axis=1)

    if dicionario_renomeacao:
        df = df.rename(columns=dicionario_renomeacao)

    df.to_csv(caminho_salvar, index=False)
    print(f"\nSucesso! O arquivo traduzido foi salvo em: {caminho_salvar}")