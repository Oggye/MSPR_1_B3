# ia/src/ml/run_pipeline.py
#
# CORRECTIF #2 : import relatif au lieu de l'import absolu "from ia.src.ml.build_dataset"
# L'import absolu fonctionnait uniquement si "ia" était dans PYTHONPATH,
# ce qui n'est pas garanti selon le mode d'exécution (module vs script direct vs Docker).
# L'import relatif est cohérent avec le reste du package.

from .build_dataset import main as build_dataset


def run():
    print("STEP 0")
    build_dataset()
    print("Dataset prêt")


if __name__ == "__main__":
    run()