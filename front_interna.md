# Front Interne ObRail Europe – Guide Complet (Version Simple)

# Objectif

Créer une interface interne destinée aux ingénieurs et équipes techniques permettant de :

* superviser l’API FastAPI
* visualiser les métriques système
* consulter les logs
* surveiller les pipelines CI/CD
* suivre les tests et la qualité de l’API
* centraliser les outils DevOps dans une seule interface React

Ce guide explique une version SIMPLE mais très professionnelle permettant de maximiser les points du projet MSPR.

---

# Architecture Finale

## Services Docker finaux

```yaml
services:
  front
  api
  db
  etl
  prometheus
  grafana
  loki
  promtail
```

---

# Rôle de chaque service

| Service    | Rôle                                |
| ---------- | ----------------------------------- |
| front      | Frontend React (client + ingénieur) |
| api        | API FastAPI                         |
| db         | Base PostgreSQL                     |
| etl        | Pipeline ETL                        |
| prometheus | Collecte métriques                  |
| grafana    | Dashboards monitoring               |
| loki       | Centralisation logs                 |
| promtail   | Collecte logs Docker                |

---

# Étape 1 — Structure des dossiers
rajouter les service Prometheus, Grafana, Loki et Promtail

# Étape 3 — Monitoring avec Prometheus

# Objectif

Prometheus va récupérer les métriques de l’API FastAPI.

Exemples :

* nombre de requêtes
* erreurs API
* temps de réponse
* disponibilité
* performance

---

# Installer prometheus-fastapi-instrumentator

Dans l’API Python :

```bash
pip install prometheus-fastapi-instrumentator
```

---

# Modifier main.py


# Résultat attendu

Prometheus pourra récupérer :

```bash
http://api:8000/metrics
```

---

# Étape 4 — Configuration Prometheus

## monitoring/prometheus/prometheus.yml


# Étape 5 — Logs centralisés avec Loki

# Objectif

Centraliser tous les logs Docker.

Exemples :

* erreurs API
* erreurs ETL
* warnings
* logs backend

---

# Configuration Loki

## monitoring/loki/local-config.yaml

# Configuration Promtail

## monitoring/promtail/config.yml

# Étape 6 — Configuration Grafana

# Objectif

Créer les dashboards DevOps.

---

# Accès

```bash
http://localhost:3001
```

Identifiants :

```text
admin
admin
```

---

# Ajouter les sources de données

## Prometheus

URL :

```text
http://prometheus:9090
```

---

## Loki

URL :

```text
http://loki:3100
```

---

# Dashboards à créer

## Dashboard API

Afficher :

* temps de réponse
* erreurs 500
* nombre requêtes
* uptime API

---

## Dashboard Docker

Afficher :

* CPU containers
* RAM containers
* état services

---

## Dashboard Logs

Afficher :

* erreurs backend
* logs ETL
* erreurs critiques

---

# Étape 7 — Structure React Front Ingénieur

# Objectif

Créer une interface interne technique.

---

# Installation React

```bash
npm create vite@latest
```

---

# Installer dépendances

```bash
npm install axios react-router-dom chart.js react-chartjs-2
```

---

# Structure React

```bash
src/
│
├── components/
│   ├── Navbar.jsx
│   ├── Sidebar.jsx
│   ├── StatusCard.jsx
│   └── MetricChart.jsx
│
├── pages/
│   ├── Dashboard.jsx
│   ├── Monitoring.jsx
│   ├── Logs.jsx
│   ├── Tests.jsx
│   ├── Pipelines.jsx
│   └── ApiHealth.jsx
│
├── services/
│   ├── api.js
│   ├── monitoring.js
│   └── github.js
│
├── layouts/
│   └── AdminLayout.jsx
│
└── App.jsx
```

---

# Étape 8 — Pages importantes du Front Ingénieur

# 1. Dashboard principal

Afficher :

* état API
* état DB
* état ETL
* uptime
* temps réponse

---

# 2. Monitoring

Afficher :

* graphiques Prometheus
* latence
* trafic API
* erreurs

---

# 3. Logs

Afficher :

* erreurs backend
* logs ETL
* logs Docker

---

# 4. Tests

Afficher :

* résultats tests API
* couverture
* dernier test exécuté

---

# 5. Pipelines CI/CD

Afficher :

* dernier pipeline GitHub Actions
* statut build
* statut déploiement
* historique pipelines

---

# Étape 9 — Endpoints FastAPI Monitoring

# Objectif

Créer des endpoints pour le front ingénieur.

---

# health.py

# metrics.py

# logs.py

# Étape 10 — GitHub Actions CI/CD

# Objectif

Automatiser :

* tests
* build Docker
* qualité
* déploiement


# Étape 11 — Tests E2E

# Objectif

Tester automatiquement le frontend.

---

# Installer Cypress

```bash
npm install cypress --save-dev
```

---

# Exemple test E2E

```javascript
describe('Dashboard', () => {
  it('loads dashboard', () => {
    cy.visit('http://localhost:3000')
    cy.contains('Dashboard')
  })
})
```

---

# Étape 12 — Dashboard DevOps Type Datadog

# Objectif

Créer une interface très professionnelle.

---

# Dashboard principal

## Sections

### Infrastructure

* API UP/DOWN
* DB UP/DOWN
* ETL Status
* Docker containers

---

### Monitoring

* trafic API
* erreurs
* latence
* CPU/RAM

---

### Logs

* erreurs critiques
* warnings
* logs temps réel

---

### CI/CD

* pipeline status
* dernier build
* version actuelle

---

### Tests

* couverture backend
* couverture frontend
* tests E2E
* dernier test

---

# Étape 13 — Front interne vs Front externe

# Front externe

Destiné aux clients.

Fonctions :

* statistiques ferroviaires
* cartes
* dashboards mobilité
* émissions CO2
* affluence

---

# Front interne

Destiné aux ingénieurs.

Fonctions :

* monitoring
* logs
* CI/CD
* qualité API
* supervision Docker
* état infrastructure
* alertes

---

# Étape 14 — Points importants pour la soutenance

# Montrer :

* séparation client / ingénieur
* monitoring temps réel
* architecture Docker propre
* industrialisation complète
* CI/CD automatisé
* supervision technique

---

# Ce qui impressionnera le jury

* dashboard DevOps live
* métriques temps réel
* logs centralisés
* pipelines visibles
* tests automatisés
* architecture microservices propre

---

# Résultat final attendu

Votre plateforme doit être :

* industrialisée
* supervisée
* monitorée
* testée
* conteneurisée
* automatisée
* maintenable
* prête pour une future IA
