# Documentation CI/CD — ObRail


## ⚠️ À faire quand les tests frontend seront prêts

1. Retirer `continue-on-error: true` du job `frontend-tests` dans le fichier ci-cd.yml
2. Mettre à jour la condition du job `docker-build` :
```yaml
   if: always() && needs.backend-tests.result == 'success' 
               && needs.frontend-tests.result == 'success'
```

## Vue d'ensemble du pipeline

```
push sur main
      │
      ├──► backend-tests    (Python / pytest)
      ├──► frontend-tests   (Node / npm)
      ├──► code-quality     (Flake8, ESLint, Prettier)
      │
      └──► docker-build ──► docker-push ──► deploy
```

## Étapes du pipeline

### 1. backend-tests
- Installe Python 3.11 et les dépendances
- Lance les tests unitaires avec `pytest`
- ❌ Si échec → pipeline bloqué

### 2. frontend-tests
- Installe Node 20 et les dépendances
- Lance les tests si présents
- ⚠️ Temporaire (le temps de rajouter des tests) : Ne bloque pas le pipeline (continue-on-error).

### 3. code-quality
- **Flake8** → vérifie le style du code Python
- **ESLint** → vérifie le code JavaScript
- **Prettier** → vérifie le formatage du code
- ⚠️ Ne bloque pas le pipeline (continue-on-error) : pour signaler les problèmes sans bloquer le pipeline.

### 4. docker-build
- Build les 3 images Docker : `api`, `front`, `etl`
- Se lance uniquement si backend-tests est vert (⚠️ En attendant la partie front tests qui devra aussi être verte)

### 5. docker-push
- Push les images sur GitHub Container Registry (GHCR)
- Images disponibles sur `ghcr.io/oggye/obrail-*:latest`

### 6. deploy
- Crée le fichier `.env` depuis les secrets GitHub
- Lance les containers avec `docker compose up`
- Vérifie que les services démarrent correctement
- Arrête les containers après vérification

## Images Docker

| Image | URL |
|---|---|
| API | `ghcr.io/oggye/obrail-api:latest` |
| Frontend | `ghcr.io/oggye/obrail-front:latest` |
| ETL | `ghcr.io/oggye/obrail-etl:latest` |

## Secrets configurés

| Nom | Usage |
|---|---|
| `GITHUB_TOKEN` | Authentification GHCR (automatique) |
| `DB_URL` | URL de la base de données | 
| `API_KEY` | Clé API de l'application |

## Comment relancer le pipeline

**Option 1 — Via un commit :**
```bash
git commit --allow-empty -m "relance pipeline"
git push origin main
```

**Option 2 — Via GitHub Actions :**
1. Onglet **Actions** sur GitHub
2. Dernier workflow → **Re-run all jobs**

## Comment débugger

1. Aller sur GitHub → onglet **Actions**
2. Cliquer sur le job en rouge
3. Lire les logs ligne par ligne
4. Erreurs fréquentes :
   - `ModuleNotFoundError` → dépendance manquante dans `requirements.txt`
   - `npm ERR!` → problème dans `package.json`
   - `denied` → problème de permissions GHCR

## Triggers

| Événement | Action |
|---|---|
| `push` sur `main` | Pipeline complet |
| `pull_request` | Pipeline complet |
