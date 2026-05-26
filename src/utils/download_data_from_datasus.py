import os
import ftplib
from typing import List, Optional

_FTP_HOST = "ftp.datasus.gov.br"

_FTP_PATHS = {
    "SIM":  "/dissemin/publicos/SIM/CID10/DORES/",
    "SIH":  "/dissemin/publicos/SIHSUS/200801_/Dados/",
    "CNES": "/dissemin/publicos/CNES/200508_/Dados/",
}

_FTP_AUX_PATHS = {
    "CNES": "/dissemin/publicos/CNES/200508_/Auxiliar/",
    "SIH":  "/dissemin/publicos/SIHSUS/200801_/Auxiliar/",
}


def download_data(
    estados: List[str],
    anos: List[int],
    meses: List[int],
    download_path: str,
    sistema: str = "SIM",
    bases_cnes: Optional[List[str]] = None
) -> None:
    if sistema not in _FTP_PATHS:
        raise ValueError(f"Sistema '{sistema}' não suportado.")

    if sistema == "CNES" and bases_cnes is None:
        raise ValueError("Para o CNES, defina a lista bases_cnes.")

    raw_dir = download_path
    ftp_path = _FTP_PATHS[sistema]

    print(f"Conectando ao FTP: {_FTP_HOST}")
    ftp = ftplib.FTP(_FTP_HOST)
    ftp.login()
    ftp.cwd(ftp_path)

    if sistema == "CNES":
        _download_cnes(ftp, ftp_path, estados, anos, meses, bases_cnes, raw_dir)
    else:
        _download_sim_sih(ftp, estados, anos, meses, sistema, raw_dir)

    ftp.quit()
    print("\nDownload finalizado!")
    print(f"Arquivos salvos em: {raw_dir}")


def download_dicionarios(sistema: str, download_path: str) -> None:
    if sistema not in _FTP_AUX_PATHS:
        raise ValueError(f"Sistema '{sistema}' não possui diretório auxiliar mapeado.")

    os.makedirs(download_path, exist_ok=True)
    aux_path = _FTP_AUX_PATHS[sistema]

    print(f"Conectando ao FTP para baixar dicionários de {sistema}: {_FTP_HOST}")
    ftp = ftplib.FTP(_FTP_HOST)
    ftp.login()
    ftp.cwd(aux_path)

    arquivos = ftp.nlst()
    arquivos_cnv = [arq for arq in arquivos if arq.lower().endswith(".cnv")]

    print(f"Encontrados {len(arquivos_cnv)} arquivos .cnv para baixar.")

    for arquivo in arquivos_cnv:
        local_path = os.path.join(download_path, arquivo)

        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            continue

        print(f"Baixando dicionário: {arquivo}")
        try:
            with open(local_path, "wb") as f:
                ftp.retrbinary(f"RETR {arquivo}", f.write)
        except ftplib.error_perm:
            if os.path.exists(local_path):
                os.remove(local_path)
            print(f"Erro ao baixar dicionário: {arquivo}")

    ftp.quit()
    print(f"\nDicionários de {sistema} salvos em: {download_path}")


def _download_cnes(
    ftp: ftplib.FTP,
    ftp_path: str,
    estados: List[str],
    anos: List[int],
    meses: List[int],
    bases_cnes: List[str],
    raw_dir: str,
) -> None:
    anos_str = [str(ano)[-2:] for ano in anos]
    meses_str = [f"{m:02d}" for m in meses]

    for base in bases_cnes:
        caminho_pasta = f"{ftp_path}{base}/"
        try:
            ftp.cwd(caminho_pasta)
        except ftplib.error_perm:
            continue

        arquivos_ftp = set(ftp.nlst())

        for estado in estados:
            for ano in anos_str:
                for mes in meses_str:
                    arquivo = f"{base}{estado}{ano}{mes}.dbc"
                    
                    if arquivo not in arquivos_ftp:
                        print(f"Arquivo não encontrado no FTP: {arquivo}")
                        continue

                    local_path = os.path.join(raw_dir, arquivo)

                    if os.path.exists(local_path):
                        if os.path.getsize(local_path) > 0:
                            continue
                        else:
                            os.remove(local_path)

                    print(f"Baixando: {arquivo}")
                    try:
                        with open(local_path, "wb") as f:
                            ftp.retrbinary(f"RETR {arquivo}", f.write)
                        print(f"Sucesso: {arquivo}")
                    except ftplib.error_perm:
                        if os.path.exists(local_path):
                            os.remove(local_path)
                        print(f"Erro ao baixar: {arquivo}")

        ftp.cwd(ftp_path)


def _download_sim_sih(
    ftp: ftplib.FTP,
    estados: List[str],
    anos: List[int],
    meses: List[int],
    sistema: str,
    raw_dir: str,
) -> None:
    meses_str = [f"{m:02d}" for m in meses]

    for estado in estados:
        for ano in anos:
            ano_curto = str(ano)[-2:]
            
            if sistema == "SIM":
                arquivos_alvo = [f"DO{estado}{ano}.dbc"]
            else:
                arquivos_alvo = [f"RD{estado}{ano_curto}{m}.dbc" for m in meses_str]

            for filename in arquivos_alvo:
                local_path = os.path.join(raw_dir, filename)

                if os.path.exists(local_path):
                    if os.path.getsize(local_path) > 0:
                        continue  
                    else:
                        os.remove(local_path)
                print(f"Baixando: {filename}")
                try:
                    with open(local_path, "wb") as f:
                        ftp.retrbinary(f"RETR {filename}", f.write)
                    print(f"Sucesso: {filename}")
                except ftplib.error_perm:
                    if os.path.exists(local_path):
                        os.remove(local_path)
                    print(f"Arquivo não encontrado: {filename}")