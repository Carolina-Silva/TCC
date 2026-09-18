import json

with open('notebooks/07_survival_analysis.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and "df_cox.drop(columns=['complexidade_cod']" in "".join(cell['source']):
        source = "".join(cell['source'])
        
        # Replace the T=0 issue and ensure complexidade_alta has variation
        fix = """df_cox.drop(columns=['complexidade_cod'], inplace=True)

# Correção para o erro de Convergência (Delta contains NaN):
# 1. Tempos exatamente iguais a 0 (óbito ou alta no mesmo dia de admissão) quebram o logaritmo em alguns casos.
df_cox.loc[df_cox['dias_permanencia'] <= 0, 'dias_permanencia'] = 0.1

# 2. Se a variável complexidade não teve variância (ex: formato de dado numérico não bateu com a string), descartamos.
if df_cox['complexidade_alta'].var() == 0:
    df_cox.drop(columns=['complexidade_alta'], inplace=True)
    print('Variável complexidade_alta removida por variância zero.')
"""
        source = source.replace("df_cox.drop(columns=['complexidade_cod'], inplace=True)", fix)
        
        cell['source'] = [line + '\n' for line in source.split('\n')]
        if cell['source'][-1] == '\n':
            cell['source'].pop()

with open('notebooks/07_survival_analysis.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
