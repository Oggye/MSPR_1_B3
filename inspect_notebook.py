import json
import pathlib
path = pathlib.Path(r'C:\Users\loadj\MSPR_1_B3\ia\src\ml\notebooks\03_explicabilite.ipynb')
nb = json.loads(path.read_text(encoding='utf-8'))
print(len(nb['cells']))
for idx, cell in enumerate(nb['cells']):
    if cell.get('cell_type') == 'code':
        src = ''.join(cell['source'])
        if 'import pandas as pd' in src or 'sys.path.insert' in src:
            print('CELL', idx)
            print(src)
            print('---')
