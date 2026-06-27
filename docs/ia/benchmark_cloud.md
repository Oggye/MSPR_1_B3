# BENCHMARK DES SERVICES D’INTELLIGENCE ARTIFICIELLE 
**Projet ObRail Europe – Prédiction de substitution avion/train**

---

## 1. INTRODUCTION

Dans le cadre du projet de développement d’un modèle prédictif pour ObRail Europe, le cahier des charges impose une étude comparative des services d’intelligence artificielle existants. L’objectif est d’évaluer les principales plateformes cloud de Machine Learning et solutions AutoML afin de justifier le choix d’une approche interne ou externalisée pour l’entraînement, l’optimisation et le déploiement du modèle.

Le projet consiste en un problème de classification binaire visant à identifier automatiquement les liaisons ferroviaires candidates à la substitution de l'avion par le train sur les trajets intra-européens. Le jeu de données issu du processus ETL d'ObRail comprend 546 enregistrements et des variables tabulaires telles que la distance, la durée, le type de train, le pays, l'opérateur et les émissions CO₂. Quatre services ont été sélectionnés pour cette analyse :

- **Amazon SageMaker (AWS)**
- **Azure Machine Learning (Microsoft)**
- **Google Vertex AI (GCP)**
- **HuggingFace AutoTrain**

L’évaluation porte sur six critères : capacités techniques, coûts, contraintes, explicabilité, facilité d’intégration et pertinence pour les données ferroviaires.

---

## 2. MÉTHODOLOGIE D’ÉVALUATION

Chaque service est évalué selon la grille suivante :

| Critère | Description |
|---------|-------------|
| **Capacités techniques** | Support des algorithmes, AutoML, personnalisation, évolutivité |
| **Coûts** | Modèle de tarification, coût estimé pour un projet de cette envergure |
| **Contraintes** | Verrouillage fournisseur, courbe d’apprentissage, dépendances |
| **Explicabilité** | Outils d’interprétabilité des modèles (SHAP, importance des variables, rapports) |
| **Facilité d’intégration** | API, SDK, déploiement, capacités MLOps |
| **Pertinence ferroviaire** | Adéquation aux données tabulaires et au besoin de classification binaire |

---

## 3. ANALYSE DÉTAILLÉE DES SERVICES

### 3.1 Amazon SageMaker (AWS)

**Présentation :** Plateforme ML entièrement gérée couvrant l’intégralité du cycle de vie. SageMaker Autopilot, sa solution AutoML, est spécialement adaptée aux données tabulaires.

**Points clés :**
- Support natif de la classification binaire sur CSV et Parquet.
- Génération de notebooks explicatifs pour chaque modèle, offrant une transparence totale; ce qui répond aux exigences de reproductibilité et de documentation du cahier des charges.
- Intégration complète avec SageMaker Pipelines, Model Registry et Feature Store pour une approche MLOps.
- **Coût :** majoration de 15 à 40 % sur les instances EC2. Tarification à la demande. Pour ce projet, les coûts d’entraînement restent modérés (quelques heures sur instances standard). Des Savings Plans peuvent réduire la facture jusqu’à 64 %.
- **Explicabilité :** notebooks générés, visualisation des features, classement des modèles, intégration SHAP possible.
- **Intégration :** SDK Boto3, interface Studio web, déploiement en un clic vers endpoints managés.
- **Pertinence :** très élevée – support natif de la classification tabulaire et transparence documentée.
- **Limite pour ce projet :** SageMaker Autopilot recommande un minimum de 500 à 1 000 lignes pour obtenir des résultats fiables. Avec 546 enregistrements, le service est techniquement utilisable mais fonctionnera en limite basse, sans garantie de qualité comparable à un entraînement sur données plus volumineuses.

### 3.2 Azure Machine Learning (Microsoft)

**Présentation :** Plateforme ML de Microsoft, proposant deux éditions (Basic et Enterprise). L’édition Enterprise inclut des outils no-code.

**Points clés :**
- AutoML (v1) supporte classification, régression et forecasting sur données tabulaires.
- **Attention :** le SDK v1 est déprécié depuis mars 2025, fin de support en juin 2026; migration vers SDK v2 obligatoire.
- **Coût :** principalement les ressources de calcul ; la plateforme elle-même est gratuite. Coûts supplémentaires pour le stockage et les services attachés. Instances GPU H100 environ 98 $/heure.
- **Explicabilité :** rapports d’évaluation et visualisations, mais moins complets que SageMaker.
- **Intégration :** excellente avec l’écosystème Microsoft (Active Directory, Power BI, Visual Studio Code).
- **Pertinence :** adapté, mais la dépréciation du SDK v1 est un risque.
- **Limite pour ce projet :** Azure ML AutoML recommande officiellement un minimum de 1 000 lignes pour la classification. Notre dataset de 546 lignes est en dessous de ce seuil, ce qui peut conduire à des modèles peu fiables ou à des erreurs lors de la validation croisée automatique.

### 3.3 Google Vertex AI (GCP)

**Présentation :** Plateforme ML unifiée de Google, intégrant AutoML, entraînement personnalisé et modèles foundation.

**Points clés :**
- AutoML pour données tabulaires supporte classification binaire et régression.
- Comprend Vertex AI Pipelines, Vector Search et l’accès aux modèles Gemini.
- **Coût :** facturation par composant (compute, entraînement, inférence). Tarifs : environ 3,46 $/heure (pour AutoML images) et 80-90 $/heure (pour H100 8-GPU). Des remises automatiques et engagements existent.
- **Risque :** facturation complexe (jusqu’à 15 services distincts) pouvant générer des surprises (certaines équipes ont rapporté des factures de 400 $ à plus de 20 000 $ en un mois).
- **Explicabilité :** outils d’analyse, mais moins mis en avant que SageMaker.
- **Intégration :** native avec BigQuery, Cloud Storage, Dataflow ; API unifiée.
- **Pertinence :** bon, mais la complexité tarifaire est un frein pour un projet académique.
- **Limite pour ce projet :** Vertex AI AutoML Tables exige un minimum de 1 000 lignes pour l'entraînement. Avec 546 enregistrements, le service refusera d'entraîner un modèle ou produira des résultats non exploitables. La complexité tarifaire est également un frein pour un projet académique.

### 3.4 HuggingFace AutoTrain

**Présentation :** Outil AutoML d’Hugging Face permettant d’entraîner, évaluer et déployer des modèles sans code.

**Points clés :**
- Support de la classification et régression tabulaires.
- Gratuit jusqu’à 10 modèles par mois ; plans payants de 0,10 à 1 $ par modèle. En local, totalement gratuit.
- **Contraintes :** moins flexible que les clouds généralistes, moins adapté aux très grands volumes, dépendance à l’écosystème Hugging Face.
- **Explicabilité :** model cards et intégration au Hub, mais moins poussée.
- **Intégration :** API simple, interface no-code, intégration avec Transformers et Datasets.
- **Pertinence pour ce projet :** contrairement aux trois services précédents, HuggingFace AutoTrain ne pose pas de seuil minimum strict sur le volume de données, ce qui le rend compatible avec notre dataset de 546 lignes. Il constitue la seule solution AutoML cloud envisageable pour une phase de prototypage.
---

## 4. SYNTHÈSE COMPARATIVE

| Critère | AWS SageMaker | Azure ML | Google Vertex AI | HuggingFace AutoTrain |
|---------|---------------|----------|------------------|------------------------|
| Modèle tarifaire | Instance + majoration 15-40% | Compute + services attachés | Composants séparés | Gratuit (10 modèles/mois) puis à la minute |
| Coût estimé (projet) | Modéré | Modéré | Élevé (risque de surprises) | Très faible |
| AutoML tabulaire | Oui (Autopilot) | Oui (v1 → v2) | Oui | Oui |
| Classification binaire | Oui | Oui | Oui | Oui |
| Explicabilité | Élevée (notebooks transparents) | Moyenne | Moyenne | Faible |
| Contrôle du modèle | Élevé | Élevé | Élevé | Limité |
| Intégration MLOps | Complète | Bonne | Bonne | Limitée |
| Verrouillage | Élevé | Élevé | Élevé | Faible |
| Courbe d’apprentissage | Moyenne | Moyenne | Élevée | Faible |
| Pertinence ferroviaire | Très élevée | Élevée | Élevée | Bonne |
| Compatible 546 lignes | ⚠️Limite basse | ❌Seuil min. 1 000 lignes | ❌Seuil min. 1 000 lignes | ✅Pas de seuil strict |

---

## 5. ANALYSE DES COÛTS CACHÉS

Les trois grands clouds partagent des postes de coûts supplémentaires souvent sous-estimés :

- **Instances inactives :** les endpoints d’inférence en temps réel facturent à l’heure, même sans usage. Pour un projet académique, cela peut représenter un surcoût significatif si l’API est maintenue active en continu.
- **Sortie de données (egress) :** transférer des données entre régions ou vers l’extérieur génère des frais qui peuvent annuler les avantages tarifaires initiaux.
- **Rareté des GPU** : la demande excédentaire pousse vers des instances plus grandes et plus chères.
- **Multiplicité des services :** Vertex AI et Azure ML facturent séparément chaque service associé (stockage, registre, monitoring), ce qui alourdit la facture globale.

---

## 6. RECOMMANDATIONS

### Choix principal : modèle interne (scikit-learn / XGBoost)

Au regard de la volumétrie du dataset ObRail (546 enregistrements), le recours aux solutions AutoML cloud présente des contraintes rédhibitoires :


1. **Azure ML et Vertex AI** imposent un seuil minimum de 1 000 lignes pour la classification tabulaire. Notre dataset ne satisfait pas cette condition, rendant ces deux services inutilisables pour ce projet.
2. **SageMaker Autopilot** fonctionne techniquement à partir de 500 lignes, mais se situe en limite basse de ses recommandations, sans garantie de fiabilité des modèles générés.
3. **HuggingFace AutoTrain** est le seul service cloud compatible sans restriction de volume, mais son explicabilité limitée et son contrôle réduit sur les algorithmes ne satisfont pas les exigences de documentation et de justification algorithmique du cahier des charges.


### Justification d’un modèle interne

Le développement d'un modèle interne avec des bibliothèques open-source (scikit-learn, XGBoost) est donc la solution retenue, pour les raisons suivantes :


- **Compatibilité avec la volumétrie :** scikit-learn et XGBoost fonctionnent sans seuil minimum de données, et sont reconnus comme particulièrement efficaces sur des datasets de taille modérée.
- **Exigence de transparence :** le cahier des charges demande une justification explicite des algorithmes et métriques. Les scripts Python versionnés et documentés répondent directement à cette exigence.
- **Reproductibilité totale :** *random_state=42*, *stratify=y*, pipelines joblib; chaque étape est traçable et reproductible sans dépendance cloud.
- **Coûts nuls :** pas de frais d'inférence cloud lors du développement et des tests.
- **Flexibilité :** possibilité d'expérimenter librement avec différents algorithmes (RandomForest, XGBoost, LightGBM, régression logistique) et d'optimiser finement les hyperparamètres via GridSearchCV ou RandomizedSearchCV.


### Alternative complémentaire  : HuggingFace AutoTrain

Si l’équipe privilégie la simplicité et la réduction des coûts d’infrastructure, HuggingFace AutoTrain constitue une alternative intéressante pour la phase de prototypage, grâce à sa gratuité partielle et sa prise en main rapide. Toutefois, son explicabilité limitée et son moindre contrôle sur les algorithmes le disqualifient pour la phase de production si les exigences de documentation sont strictes.

---

## 7. SOURCES

1. AWS. (2026). *SageMaker Pricing*. https://aws.amazon.com/sagemaker/pricing/
2. AWS. (2026). *Amazon SageMaker Autopilot*. https://www.amazonaws.cn/en/sagemaker/autopilot/
3. Redress Compliance. (2026). *SageMaker vs Azure ML vs Vertex AI: The Cost Comparison*. https://redresscompliance.com/aws-sagemaker-vs-azure-ml-vs-vertex-ai-comparison
4. CloudZero. (2026). *Google Vertex AI Pricing: Complete Enterprise Guide*. https://www.cloudzero.com/blog/google-vertex-ai-pricing/
5. Nops.io. (2026). *Vertex AI Pricing: The Complete 2026 Guide*. https://www.nops.io/blog/vertex-ai-pricing/
6. CloudZero. (2026). *Cloud GPU Pricing Comparison: AWS Vs Azure Vs GCP*. https://www.cloudzero.com/blog/cloud-gpu-pricing-comparison/
7. Hugging Face. (2026). *AutoTrain Documentation*. https://huggingface.co/autotrain
8. Hugging Face. (2026). *AutoTrain Pricing*. https://huggingface.co/pricing
9. Microsoft. (2026). *Azure Machine Learning Pricing*. https://azure.microsoft.com/pricing/details/machine-learning/
10. Microsoft. (2026). *What is automated ML? AutoML (v1)*. https://learn.microsoft.com/azure/machine-learning/concept-automated-ml
11. Google Cloud. (2026). *Vertex AI AutoML Documentation*. https://cloud.google.com/vertex-ai/docs/automl
