import json
import pathlib
path = pathlib.Path(r'C:\Users\loadj\MSPR_1_B3\ia\src\ml\notebooks\03_explicabilite.ipynb')
nb = json.loads(path.read_text(encoding='utf-8'))
source = nb['cells'][1]['source']
cleaned = []
inserted = False
for line in source:
    if line.startswith('import warnings') or line.startswith('warnings.filterwarnings'):
        if not inserted:
            if line.startswith('import warnings'):
                cleaned.append('import warnings\n')
                cleaned.append('warnings.filterwarnings("ignore", message=r".*Trying to unpickle estimator Ridge.*")\n')
                cleaned.append('warnings.filterwarnings("ignore", message=r".*feature_perturbation option is now deprecated.*")\n')
                inserted = True
        continue
    cleaned.append(line)
# if we didn't insert and import shap exists, insert after it
if not inserted:
    result=[]
    for line in cleaned:
        result.append(line)
        if line.strip() == 'import shap':
            result.append('\n')
            result.append('import warnings\n')
            result.append('warnings.filterwarnings("ignore", message=r".*Trying to unpickle estimator Ridge.*")\n')
            result.append('warnings.filterwarnings("ignore", message=r".*feature_perturbation option is now deprecated.*")\n')
    cleaned=result
nb['cells'][1]['source'] = cleaned
path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding='utf-8')
print('cleaned')
