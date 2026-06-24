import json
import pathlib
path = pathlib.Path(r'C:\Users\loadj\MSPR_1_B3\ia\src\ml\notebooks\03_explicabilite.ipynb')
nb = json.loads(path.read_text(encoding='utf-8'))
paths = []
for i, cell in enumerate(nb.get('cells', [])):
    def rec(prefix, o):
        if isinstance(o, str) and 'C:\\Users\\loadj' in o:
            paths.append((i, prefix, o))
        elif isinstance(o, dict):
            for kk, vv in o.items():
                rec(f'{prefix}.{kk}' if prefix else kk, vv)
        elif isinstance(o, list):
            for jj, vv in enumerate(o):
                rec(f'{prefix}[{jj}]', vv)
    rec('', cell)
print('found', len(paths))
for p in paths[:20]:
    print(p)
