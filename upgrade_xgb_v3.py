import json
import re

with open('notebooks/06_predictive_modeling.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'xgb_model = XGBClassifier(' in "".join(cell['source']):
        source = "".join(cell['source'])
        
        # We want to ensure:
        # max_depth=10
        # colsample_bytree=0.5
        
        source = re.sub(r"max_depth=\d+,", "max_depth=10,", source)
        source = re.sub(r"colsample_bytree=0.\d+,", "colsample_bytree=0.5,", source)
        
        # If the comments got messed up or I want to be safe, I just replace the specific strings:
        
        cell['source'] = [line + '\n' for line in source.split('\n')]
        if cell['source'][-1] == '\n':
            cell['source'].pop()

with open('notebooks/06_predictive_modeling.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
