import json

with open('notebooks/06_predictive_modeling.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'xgb_model = XGBClassifier(' in "".join(cell['source']):
        source = "".join(cell['source'])
        
        # Replace the XGB parameters again
        source = source.replace("max_depth=8", "max_depth=10")
        source = source.replace("colsample_bytree=0.8", "colsample_bytree=0.5")
        
        cell['source'] = [line + '\n' for line in source.split('\n')]
        if cell['source'][-1] == '\n':
            cell['source'].pop()

with open('notebooks/06_predictive_modeling.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
