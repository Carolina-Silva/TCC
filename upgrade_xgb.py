import json

with open('notebooks/06_predictive_modeling.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'xgb_model = XGBClassifier(' in "".join(cell['source']):
        source = "".join(cell['source'])
        
        # Replace the XGB parameters
        import re
        source = re.sub(r"n_estimators=300,", "n_estimators=1200, # Aumentado para mais aprendizado", source)
        source = re.sub(r"max_depth=6,", "max_depth=8, # Aumentado (temos muitos dados)", source)
        source = re.sub(r"learning_rate=0.05,", "learning_rate=0.02, # Passos menores", source)
        
        # Add min_child_weight to avoid overfitting
        source = source.replace("scale_pos_weight=scale_pos_weight,", "min_child_weight=10, # Evita overfit nas folhas profundas\n    scale_pos_weight=scale_pos_weight,")
        
        cell['source'] = [line + '\n' for line in source.split('\n')]
        if cell['source'][-1] == '\n':
            cell['source'].pop()

with open('notebooks/06_predictive_modeling.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
