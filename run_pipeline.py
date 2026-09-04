import os
import subprocess
import time
from pathlib import Path

def run_notebook(notebook_path, log_file):
    print(f"\n[{time.strftime('%H:%M:%S')}] Executando: {notebook_path.name}")
    log_file.write(f"\n{'='*50}\n")
    log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando {notebook_path.name}\n")
    log_file.flush()

    try:
        # Executa via nbconvert in-place
        result = subprocess.run(
            ["jupyter", "nbconvert", "--execute", "--inplace", str(notebook_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            print(f"[{time.strftime('%H:%M:%S')}] ✓ SUCESSO: {notebook_path.name}")
            log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✓ SUCESSO\n")
            return True
        else:
            print(f"[{time.strftime('%H:%M:%S')}] ✗ FALHA: {notebook_path.name} (veja pipeline_run.log)")
            log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ FALHA\n")
            log_file.write("--- ERRO TRACEBACK ---\n")
            log_file.write(result.stderr)
            log_file.write("----------------------\n")
            return False

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ✗ ERRO CRÍTICO ao tentar executar {notebook_path.name}: {e}")
        log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ ERRO CRÍTICO\n")
        log_file.write(str(e) + "\n")
        return False

def main():
    root_dir = Path(__file__).parent.resolve()
    notebooks_dir = root_dir / "notebooks"
    log_path = root_dir / "pipeline_run.log"

    # Sequência exata de execução
    notebooks = [
        # "01a_data_collection.ipynb",  # Pulado para não demorar na validação dos downloads
        "01b_data_translation.ipynb",
        "02_etl_ database_integration.ipynb",
        "03_merge_and_eda.ipynb",
        "04_analysis_exploration_visualization.ipynb",
        "05_feature_selection.ipynb",
        "06_predictive_modeling.ipynb",
        "07_survival_analysis.ipynb"
    ]

    print("==================================================")
    print("      INICIANDO PIPELINE DE DADOS TCC IAM         ")
    print("==================================================")

    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"Início da execução da pipeline: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        start_total = time.time()
        for nb_name in notebooks:
            nb_path = notebooks_dir / nb_name
            
            if not nb_path.exists():
                print(f"\n[AVISO] Notebook não encontrado: {nb_name}. Pulando...")
                log_file.write(f"\n[AVISO] Notebook não encontrado: {nb_name}\n")
                continue

            start_time = time.time()
            sucesso = run_notebook(nb_path, log_file)
            end_time = time.time()
            
            duracao = end_time - start_time
            print(f"   Duração: {duracao/60:.1f} minutos")
            log_file.write(f"Duração: {duracao/60:.1f} minutos\n")

            if not sucesso:
                print("\n[!] Pipeline abortada devido a erro. Verifique pipeline_run.log.")
                break

        total_duracao = time.time() - start_total
        print(f"\nTempo total de execução: {total_duracao/60:.1f} minutos.")
        log_file.write(f"\nFim da execução. Tempo total: {total_duracao/60:.1f} minutos.\n")

if __name__ == "__main__":
    main()
