import pandas as pd
from lifelines import CoxPHFitter
import numpy as np

df = pd.read_csv('../data/processed/base_modelagem.csv', low_memory=False, nrows=100000)
df['indicador_obito'] = pd.to_numeric(df['indicador_obito'], errors='coerce')
df['dias_permanencia'] = pd.to_numeric(df.get('quantidade_diarias', df.get('dias_permanencia', 0)), errors='coerce')
df_enr = pd.read_csv('../data/processed/base_modelagem_enriched.csv', usecols=['escore_estrutura'], low_memory=False, nrows=100000)
df['escore_estrutura'] = df_enr['escore_estrutura'].values

cols_cox = ['dias_permanencia', 'indicador_obito', 'idade', 'sexo', 'carater_internacao', 'complexidade_cod', 'escore_estrutura']
df_cox = df[cols_cox].copy().dropna()

df_cox['sexo'] = (df_cox['sexo'] == 'Feminino').astype(int)
df_cox['carater_internacao'] = (df_cox['carater_internacao'] == 'Urgência').astype(int)
df_cox['complexidade_alta'] = (df_cox['complexidade_cod'].astype(str).str.contains('03|Alta', case=False, na=False)).astype(int)
df_cox.drop(columns=['complexidade_cod'], inplace=True)

df_cox.loc[df_cox['dias_permanencia'] > 30, 'indicador_obito'] = 0
df_cox['dias_permanencia'] = df_cox['dias_permanencia'].clip(upper=30)

# Also fix T=0
df_cox.loc[df_cox['dias_permanencia'] == 0, 'dias_permanencia'] = 0.5

print("Variances:")
print(df_cox.var())

print("\nCollinearity check:")
print(df_cox.corr())

try:
    cph = CoxPHFitter()
    cph.fit(df_cox, duration_col='dias_permanencia', event_col='indicador_obito')
    print("Success")
except Exception as e:
    print(f"Error: {e}")
