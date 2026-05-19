# Projet MSPR – ObRail Europe

## 📌 Présentation

ObRail Europe est une plateforme d’analyse de la mobilité ferroviaire européenne développée dans le cadre de la MSPR B3.

Le projet centralise des données ferroviaires européennes via un pipeline ETL, les stocke dans un entrepôt PostgreSQL, puis les expose via une API REST et plusieurs interfaces React.

La documentation technique complète du projet est disponible dans :

```txt
docs/rapport_technique.md
```

---

# 🚀 Démarrage rapide

## 1. Prérequis

Avant de commencer, installer :

* Docker
* Docker Compose
* Git

Optionnel pour le développement local :

* Node.js 20+
* Python 3.11+

---

## 2. Récupération du projet

### Cloner le dépôt

```bash
git clone https://github.com/Oggye/MSPR_1_B3
```

### Entrer dans le projet

```bash
cd MSPR_1_B3
```

---

## 3. Initialisation du projet

### Lancer tous les services

```bash
docker compose up --build
```

### Vérifier les conteneurs

```bash
docker compose ps
```

### Voir les logs en temps réel

```bash
docker compose logs -f
```

### Arrêter le projet

```bash
docker compose down
```

---

# 🌐 URLs importantes

| Service               | URL                              |
| --------------------- | -------------------------------- |
| Frontend React        | `http://localhost:3000`          |
| API FastAPI           | `http://localhost:8000`          |
| Documentation Swagger | `http://localhost:8000/api/docs` |
| Grafana               | `http://localhost:3001`          |
| Prometheus            | `http://localhost:9090`          |
| PostgreSQL            | `localhost:5432`                 |

---

# 🧱 Stack technique

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

## Frontend

* React
* Axios
* Leaflet
* Chart.js

## Data / ETL

* Python
* Pandas

## Infra / DevOps

* Docker
* Docker Compose
* GitHub Actions
* Grafana
* Prometheus
* Loki
* Promtail

---

# 📂 Structure principale

```txt
MSPR_1_B3/
│
├── docker-compose.yml
├── README.md
├── docs/
├── data/
├── etl/
├── monitoring/
├── platform/
├── sql/
└── .github/
```

---

# 🧪 Tests

## Backend

```bash
python -m pytest -v platform/server/test/unit
```

## Frontend E2E

```bash
cd platform/front/app

npm ci
npm run e2e:install
npm run e2e
```

---

# 📊 Monitoring

Le projet intègre une stack complète de supervision :

* Grafana
* Prometheus
* Loki
* Promtail

Les dashboards Grafana sont automatiquement provisionnés depuis :

```txt
monitoring/grafana/dashboards/
```

---

# 📖 Documentation

Documentation technique complète :

```txt
docs/rapport_technique.md
```

Contient notamment :

* Architecture globale
* Pipeline ETL
* Base de données
* API REST
* CI/CD
* Tests
* Monitoring
* Sécurité
* RGPD
* Accessibilité
* Maintenance & rollback

---

# 👥 Équipe

* ABDILLAHI ABDI Mariam Marwo
* SAMB Adja Nafissatou Lo
* NKIBAN A ITCHIRI Orlane Emmanuelle Andrea
* TOURE Zeinab Anne Marie
* NDIAYE Mansour Djamil

Suivi projet :
[Trello MSPR B3](https://trello.com/invite/b/69e74e583f650936f382ba17/ATTIaa05d72d0f16e3a2a3827bc407c678ffA9A7D7CE/mspr-b3?utm_source=chatgpt.com)

---

# ✅ Commandes utiles

```bash
# Rebuild complet
docker compose up --build

# Logs
docker compose logs -f

# Etat des services
docker compose ps

# Stopper les services
docker compose down

# Stopper + supprimer volumes
docker compose down -v
```
