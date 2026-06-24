import json
import pathlib
path = pathlib.Path(r'C:\Users\loadj\MSPR_1_B3\ia\src\ml\notebooks\03_explicabilite.ipynb')
nb = json.loads(path.read_text(encoding='utf-8'))
cell = nb['cells'][1]
source = cell['source']
insert_lines = [
    'import warnings\n',
    'warnings.filterwarnings("ignore", message=r".*Trying to unpickle estimator Ridge.*")\n',
    'warnings.filterwarnings("ignore", message=r".*feature_perturbation option is now deprecated.*")\n',
]
# Insert after imports
for i, line in enumerate(source):
    if line.strip() == 'import shap':
        source.insert(i+1, '\n')
        source.insert(i+2, insert_lines[0])
        source.insert(i+3, insert_lines[1])
        source.insert(i+4, insert_lines[2])
        break
cell['source'] = source
path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding='utf-8')
print('updated')
