"""
src/build_external_dicts.py
────────────────────────────────────────────────────────────────────────────
Cria os arquivos de dicionário em data/external/ para decodificar os
códigos numéricos do CNES e SIH.

Execute uma vez:
    python src/build_external_dicts.py

Outputs:
    data/external/cnes_instalacoes.csv      → qtd_instalacao_XX
    data/external/cnes_natureza_juridica.csv
    data/external/sih_especialidade_leito.csv
    data/external/sih_carater_internacao.csv
    data/external/sih_complexidade.csv
"""

import pandas as pd
from pathlib import Path

EXTERNAL = Path("data/external")
EXTERNAL.mkdir(parents=True, exist_ok=True)


# ── 1. Instalações CNES ───────────────────────────────────────────────────────
# Fonte: Dicionário de Dados CNES — tabela tb_tipo_instalacao
instalacoes = pd.DataFrame([
    (1,  "Consultório"),
    (2,  "Sala de Reunião/Estudo"),
    (3,  "Sala de Espera"),
    (4,  "Banheiro Adaptado para PCD"),
    (5,  "Farmácia"),
    (6,  "Almoxarifado de Medicamentos"),
    (7,  "Central de Material Esterilizado"),
    (8,  "Lavanderia"),
    (9,  "Necrotério"),
    (10, "Sala de Inalação/Nebulização"),
    (11, "Sala de Imunização/Vacina"),
    (12, "Sala de Curativos"),
    (13, "Sala de Gesso"),
    (14, "Sala de Parto Normal"),
    (15, "Sala de Pré-Parto"),
    (16, "Sala de Cirurgia/Centro Cirúrgico"),
    (17, "Sala de Cirurgia Ambulatorial"),       # qtd_instalacao_17
    (18, "Centro Obstétrico"),
    (19, "Sala de Endoscopia"),
    (20, "Sala de Hemodiálise"),
    (21, "Sala de Quimioterapia"),
    (22, "Sala de Recuperação Pós-Anestésica"),  # qtd_instalacao_22
    (23, "Sala de Raios-X"),
    (24, "Sala de Ultrassonografia"),
    (25, "Sala de Tomografia Computadorizada"),
    (26, "Sala de Ressonância Magnética"),
    (27, "Sala de Mamografia"),
    (28, "Sala de Densitometria Óssea"),
    (29, "Sala de Hemodinâmica"),                # qtd_instalacao_29 ← IAM
    (30, "Sala de Radioterapia"),
    (31, "Sala de Medicina Nuclear"),            # qtd_instalacao_31
    (32, "Banco de Sangue/Hemoterapia"),
    (33, "UTI Adulto"),                          # qtd_instalacao_33 ← IAM
    (34, "UTI Pediátrica"),
    (35, "UTI Neonatal"),
    (36, "UTI Queimados"),
    (37, "UTI Coronariana (UCO)"),
    (38, "Unidade de Isolamento"),
    (39, "Banco de Leite Humano"),
    (40, "Centro de Atenção Psicossocial (CAPS)"),
    (41, "Sala de Procedimentos Odontológicos"),
    (42, "Sala de Coleta"),
    (43, "Sala de Fisioterapia/Reabilitação"),
], columns=["codigo", "descricao"])

instalacoes.to_csv(EXTERNAL / "cnes_instalacoes.csv", index=False)
print(f"✓ cnes_instalacoes.csv ({len(instalacoes)} registros)")

# Destaca os relevantes para IAM
relevantes = instalacoes[instalacoes["codigo"].isin([17, 22, 29, 31, 33])]
print("\n  Instalações presentes na sua base:")
for _, row in relevantes.iterrows():
    print(f"    qtd_instalacao_{row['codigo']:02d} → {row['descricao']}")


# ── 2. Natureza Jurídica ──────────────────────────────────────────────────────
# Fonte: Tabela de Natureza Jurídica — IBGE/CNES
natureza = pd.DataFrame([
    (1023, "Empresa Pública"),
    (1031, "Empresa de Economia Mista"),
    (1040, "Empresa Privada"),
    (1058, "Empresa Individual"),
    (1066, "Empresa Individual de Responsabilidade Limitada"),
    (1074, "Empresa Individual Imobiliária"),
    (1082, "Empresa com Sócio-Gerente"),
    (1104, "Empresa Inativa"),
    (2011, "Órgão Público do Poder Executivo Federal"),
    (2038, "Órgão Público do Poder Executivo Estadual"),
    (2046, "Órgão Público do Poder Executivo Municipal"),
    (2054, "Órgão Público do Poder Legislativo Federal"),
    (2062, "Órgão Público do Poder Judiciário Federal"),
    (3034, "Autarquia Federal"),
    (3069, "Fundação Pública de Direito Público Federal"),  # aparece na sua base
    (3077, "Fundação Pública de Direito Público Estadual"),
    (3085, "Fundação Pública de Direito Público Municipal"),
    (3093, "Fundação Pública de Direito Privado"),
    (3999, "Outras Fundações Públicas"),
    (4014, "Autarquia Estadual"),
    (4022, "Autarquia Municipal"),
    (5010, "Associação Privada"),
    (5029, "Fundação Privada"),
    (5037, "Organização Religiosa"),
    (5045, "Organização Social (OS)"),
    (5053, "Organização da Sociedade Civil de Interesse Público (OSCIP)"),
    (5061, "Sindicato"),
    (5070, "Entidade Sindical"),
    (5088, "Federação"),
    (5096, "Confederação"),
    (5118, "Partido Político"),
    (5126, "Entidade de Fiscalização do Exercício das Profissões"),
    (5134, "Fundo Privado"),
    (5142, "Órgão de Direção Nacional de Partido Político"),
    (5150, "Serviço Social Autônomo"),
    (5169, "Comissão de Conciliação Prévia"),
    (5177, "Entidade Fechada de Previdência Complementar"),
    (6017, "Empresa Individual de Responsabilidade Limitada (EIRELI)"),
    (8885, "Natureza Jurídica não informada"),
], columns=["codigo", "descricao"])

# Cria agrupamento macro (útil para modelagem)
def macro_natureza(cod):
    if 2000 <= cod <= 4999:
        return "Público"
    elif cod in (5045, 5053):
        return "OS/OSCIP"
    elif cod in (5010, 5029, 5037):
        return "Privado sem fins lucrativos"
    elif cod >= 5000:
        return "Privado com fins lucrativos"
    else:
        return "Outro"

natureza["macro"] = natureza["codigo"].apply(macro_natureza)
natureza.to_csv(EXTERNAL / "cnes_natureza_juridica.csv", index=False)
print(f"\n✓ cnes_natureza_juridica.csv ({len(natureza)} registros)")

# Valor 3069 aparece na base do usuário
linha_3069 = natureza[natureza["codigo"] == 3069]
if not linha_3069.empty:
    print(f"  natureza_juridica=3069 → {linha_3069.iloc[0]['descricao']} ({linha_3069.iloc[0]['macro']})")


# ── 3. Especialidade do Leito (SIH) ──────────────────────────────────────────
especialidade_leito = pd.DataFrame([
    (1,  "Cirurgia"),
    (2,  "Obstetrícia"),
    (3,  "Clínica Médica"),
    (4,  "Pediatria"),
    (5,  "Psiquiatria"),
    (6,  "Pneumologia Sanitária"),
    (7,  "Complementar (UTI/UCO/etc)"),
], columns=["codigo", "descricao"])

especialidade_leito.to_csv(EXTERNAL / "sih_especialidade_leito.csv", index=False)
print(f"\n✓ sih_especialidade_leito.csv")
print("  Valores possíveis:", especialidade_leito.set_index("codigo")["descricao"].to_dict())


# ── 4. Caráter de Internação (SIH) ────────────────────────────────────────────
carater = pd.DataFrame([
    (1, "Eletivo"),
    (2, "Urgência"),
    (3, "Acidente no Local de Trabalho ou a Serviço da Empresa"),
    (4, "Acidente no Trajeto para o Trabalho"),
    (5, "Outros Tipos de Acidentes de Trânsito"),
    (6, "Outros Tipos de Lesões e Envenenamentos por Agentes Externos"),
], columns=["codigo", "descricao"])

carater.to_csv(EXTERNAL / "sih_carater_internacao.csv", index=False)
print(f"\n✓ sih_carater_internacao.csv")
print("  Valores:", carater.set_index("codigo")["descricao"].to_dict())


# ── 5. Complexidade (SIH) ─────────────────────────────────────────────────────
complexidade = pd.DataFrame([
    (1, "Atenção Básica"),
    (2, "Média Complexidade"),
    (3, "Alta Complexidade"),
], columns=["codigo", "descricao"])

complexidade.to_csv(EXTERNAL / "sih_complexidade.csv", index=False)
print(f"\n✓ sih_complexidade.csv")


print("\n" + "─"*50)
print("Todos os dicionários salvos em data/external/")
print("\nPróximo passo: use pd.merge() para decodificar as colunas")
print("antes de plotar. Exemplo:")
print("  df = df.merge(instalacoes.rename(columns={'codigo':'cod','descricao':'nome_instalacao'}),")
print("                left_on='qtd_instalacao_29', right_on='cod', how='left')")
