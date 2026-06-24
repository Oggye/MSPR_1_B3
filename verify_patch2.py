import json
import pathlib
path = pathlib.Path(r'C:\Users\loadj\MSPR_1_B3\ia\src\ml\notebooks\03_explicabilite.ipynb')
nb = json.loads(path.read_text(encoding='utf-8'))
print(''.join(nb['cells'][1]['source']))
