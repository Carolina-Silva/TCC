import os
import ftplib
from typing import List

# Mapeamento dos caminhos FTP por sistema
_FTP_HOST = "ftp.datasus.gov.br"

_FTP_PATHS = {
    "SIM":  "/dissemin/publicos/SIM/CID10/DORES/",
    "SIH":  "/dissemin/publicos/SIHSUS/200801_/Dados/",
    "CNES": "/dissemin/publicos/CNES/200508_/Dados/",
}


def download_data(
    estados: List[str] = None,
    anos: List[int] = None,
    sistema: str = "SIM",
    download_path: str = None,
) -> None:
    """Baixa arquivos .dbc do DataSUS via FTP para um diretório local.

    Parameters
    ----------
    estados : List[str]
        Siglas dos estados brasileiros a baixar (ex.: ``["SP", "RJ"]``).
    anos : List[int]
        Anos de referência dos dados (ex.: ``[2022, 2023]``).
    sistema : str
        Sistema do DataSUS a consultar. Aceita: ``"SIM"``, ``"SIH"`` ou
        ``"CNES"``. Padrão: ``"SIM"``.
    download_path : str
        Caminho do diretório local onde os arquivos serão salvos.
        O diretório deve existir antes da chamada.

    Raises
    ------
    ValueError
        Se ``sistema`` não for um dos valores suportados.

    Notes
    -----
    - Arquivos já existentes com tamanho > 0 não são baixados novamente.
    - Arquivos corrompidos (tamanho = 0) são removidos e re-baixados.
    - Para o sistema CNES, os dados são organizados em subpastas no FTP;
      a função navega por essas subpastas automaticamente.
    """
    if sistema not in _FTP_PATHS:
        raise ValueError(
            f"Sistema '{sistema}' não suportado. "
            f"Escolha entre: {list(_FTP_PATHS.keys())}"
        )

    raw_dir = download_path
    ftp_path = _FTP_PATHS[sistema]

    print(f"Conectando ao FTP: {_FTP_HOST}")
    ftp = ftplib.FTP(_FTP_HOST)
    ftp.login()
    ftp.cwd(ftp_path)

    if sistema == "CNES":
        _download_cnes(ftp, ftp_path, estados, anos, raw_dir)
    else:
        _download_sim_sih(ftp, estados, anos, sistema, raw_dir)

    ftp.quit()
    print("\nDownload finalizado!")
    print(f"Arquivos salvos em: {raw_dir}")


def _download_cnes(
    ftp: ftplib.FTP,
    ftp_path: str,
    estados: List[str],
    anos: List[int],
    raw_dir: str,
) -> None:
    """Percorre as subpastas do CNES no FTP e baixa os arquivos filtrados."""
    anos_str = [str(ano)[-2:] for ano in anos]
    pastas = ftp.nlst()

    for pasta in pastas:
        caminho_pasta = f"{ftp_path}{pasta}/"
        ftp.cwd(caminho_pasta)
        arquivos = ftp.nlst()

        for arquivo in arquivos:
            if not arquivo.endswith(".dbc"):
                continue

            if not any(estado in arquivo for estado in estados):
                continue

            if not any(ano in arquivo for ano in anos_str):
                continue

            local_path = os.path.join(raw_dir, arquivo)
            if os.path.exists(local_path):
                continue 

            try:
                with open(local_path, "wb") as f:
                    ftp.retrbinary(f"RETR {arquivo}", f.write)
            except Exception:
                pass

        ftp.cwd(ftp_path)


def _download_sim_sih(
    ftp: ftplib.FTP,
    estados: List[str],
    anos: List[int],
    sistema: str,
    raw_dir: str,
) -> None:
    """Baixa arquivos mensais do SIM ou SIH para os estados e anos pedidos."""
    meses = [f"{m:02d}" for m in range(1, 13)]

    for estado in estados:
        for ano in anos:
            ano_curto = str(ano)[-2:]
            for mes in meses:
                if sistema == "SIM":
                    filename = f"DO{estado}{ano}.dbc"
                else:  # SIH
                    filename = f"RD{estado}{ano_curto}{mes}.dbc"

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
