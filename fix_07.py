import json

with open('notebooks/07_survival_analysis.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and "T = df['dias_permanencia']" in "".join(cell['source']):
        source = "".join(cell['source'])
        new_source = source.replace("T = df['dias_permanencia']  # Tempo", "T = df['dias_permanencia'].clip(upper=30)  # Tempo (Corte clínico de 30 dias)")
        new_source = new_source.replace("E = df['indicador_obito']   # Evento", "E = df['indicador_obito']\nE = E.where(df['dias_permanencia'] <= 30, 0) # Censura pacientes que ficaram mais de 30 dias (Foco em mortalidade aguda de 30 dias)")
        
        cell['source'] = [line + '\n' for line in new_source.split('\n')]
        if cell['source'][-1] == '\n':
            cell['source'].pop()

    if cell['cell_type'] == 'code' and "cols_cox = ['dias_permanencia'" in "".join(cell['source']):
        source = "".join(cell['source'])
        # Add complexidade to cox
        new_source = source.replace("cols_cox = ['dias_permanencia', 'indicador_obito', 'idade', 'sexo', 'carater_internacao', 'escore_estrutura']",
                                    "cols_cox = ['dias_permanencia', 'indicador_obito', 'idade', 'sexo', 'carater_internacao', 'complexidade_cod', 'escore_estrutura']")
        
        new_source = new_source.replace("df_cox['carater_internacao'] = (df_cox['carater_internacao'] == 'Urgência').astype(int)",
                                        "df_cox['carater_internacao'] = (df_cox['carater_internacao'] == 'Urgência').astype(int)\ndf_cox['complexidade_alta'] = (df_cox['complexidade_cod'].astype(str).str.contains('03|Alta', case=False, na=False)).astype(int)\ndf_cox.drop(columns=['complexidade_cod'], inplace=True)")
        
        # Also apply 30 day censor to cox dataframe
        new_source = new_source.replace("df_cox = df[cols_cox].copy().dropna()",
                                        "df_cox = df[cols_cox].copy().dropna()\ndf_cox.loc[df_cox['dias_permanencia'] > 30, 'indicador_obito'] = 0\ndf_cox['dias_permanencia'] = df_cox['dias_permanencia'].clip(upper=30)")
        
        cell['source'] = [line + '\n' for line in new_source.split('\n')]
        if cell['source'][-1] == '\n':
            cell['source'].pop()

with open('notebooks/07_survival_analysis.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
