# 8. Veille, Justification et Communication Projet

## Synthèse exécutive

La veille réalisée dans le cadre du projet ObRail Europe couvre trois axes stratégiques : **algorithmique** (performance et interprétabilité des modèles), **réglementaire** (conformité RGPD et AI Act) et **sécurité** (robustesse des modèles et protection des données). Chaque axe est illustré par des **exemples concrets issus des livrables du projet** et des **sources**, conformément aux exigences du cahier des charges.

## Axe 1 — Veille Algorithmique

### 1.1 Tendances et évolutions des modèles utilisés

#### XGBoost : référence confirmée en 2026

**Contexte projet** : Dans le cadre de la **détection des pays en déclin** (classification `en_declin`), XGBoost a été retenu comme modèle final après optimisation, atteignant un **F1-Score de 0,667** et un **ROC-AUC de 0,826** sur le jeu de test (`rapport_evaluation.md`). L'optimisation par `RandomizedSearchCV` a permis de passer d'un F1 de 0,610 à 0,667, soit un gain de **+9,3 %**.

**Tendances** : La recherche confirme la pertinence durable de XGBoost pour les données tabulaires. Une étude de mars 2026 (*XGenBoost*) démontre que les ensembles d'arbres comme XGBoost restent préférés pour les tâches discriminatives sur données tabulaires de types mixtes, en raison de leurs **biais inductifs** (capacité à capturer des relations non-linéaires sans hypothèse forte sur la distribution des données), de leur **paramétrage minimal** et de leur **efficacité d'entraînement**. Les auteurs proposent même XGenBoost, un modèle génératif basé sur XGBoost, adapté aux **petits datasets** comme celui d'ObRail (546 observations).

Une autre étude de janvier 2026 (*Nature*) confirme la performance de XGBoost avec une AUC de **0,95** et une **Accuracy de 0,92** en validation croisée 10-fold. Ces résultats sont cohérents avec les performances obtenues sur le projet ObRail.

#### Ridge : modèle linéaire toujours pertinent

**Contexte projet** : Pour la **prévision de fréquentation ferroviaire** (régression `passengers`), le modèle Ridge baseline a surperformé toutes les autres méthodes avec un **R² de 0,9962** et un **MAE de 4 339** (`rapport_evaluation.md`). Ce résultat s'explique par la **forte autocorrélation temporelle** des séries de fréquentation : la relation entre `passengers_lag1`, `passengers_lag2` et `passengers` est quasi-linéaire.

**Tendances** : Les modèles hybrides combinant Ridge avec d'autres méthodes font l'objet de recherches actives. Une étude de mai 2026 (*Applied Soft Computing*) intègre Ridge Regression, Kernel Ridge Regression et LASSO dans un **ensemble linéaire** pour la prédiction d'épidémies, obtenant des corrélations de **R = 0,98** sur des données complexes. Une autre étude de mars 2026 propose un **ensemble de stacking** où Ridge est utilisé comme **méta-apprenant** (combinaison des prédictions de plusieurs modèles de base comme LightGBM et Random Forest).

**Recommandation** : Pour ObRail, l'exploration d'un **modèle hybride Ridge-XGBoost** (utilisant Ridge comme méta-apprenant des prédictions de XGBoost) pourrait améliorer encore la robustesse sur les petits pays où la variance est plus élevée.

### 1.2 Explicabilité et interprétabilité

**Contexte projet** : Le notebook `03_explicabilite.ipynb` a produit des visualisations SHAP pour les deux modèles retenus :
- **Classification** : `fig_shap_clf.png` confirme que `passengers_lag1` et `passengers_lag2` sont les variables les plus influentes, suivies de `co2_per_passenger`.
- **Régression** : `fig_shap_reg.png` montre que `num_passengers_lag1` et `num_passengers_lag2` dominent largement les prédictions.

**État de l'art** : SHAP reste la méthode de référence pour l'interprétation des modèles. Une étude de mars 2026 (*arXiv*) sur la détection de textes générés par IA montre que **XGBoost avec analyse stylométrique atteint des performances comparables aux modèles de deep learning tout en restant interprétable**. Cette interprétabilité est un avantage clé pour ObRail, qui doit justifier ses prédictions auprès des institutions européennes et des opérateurs ferroviaires.

**Bonnes pratiques** : Le cahier des charges ObRail impose la **reproductibilité** via la fixation des graines aléatoires (`random_state=42`), la documentation des étapes et la structuration cohérente du projet. Ces principes ont été respectés : tous les scripts utilisent `random_state=42`, les modèles sont sauvegardés en `.joblib` et les métriques en `.json`.

### 1.3 Benchmark des services IA

**Contexte projet** : Le fichier `benchmark_cloud.md` compare quatre services : **AWS SageMaker**, **Azure ML**, **Google Vertex AI** et **HuggingFace AutoTrain**. Le choix d'**AWS SageMaker** est justifié par :
- **Explicabilité** : génération automatique de notebooks par SageMaker Autopilot, répondant aux exigences de transparence du cahier des charges.
- **Support natif** de la classification tabulaire.
- **Coûts maîtrisés** : pour une volumétrie modérée (546 observations), les coûts d'entraînement restent raisonnables.

**Tendances** : Une analyse d'avril 2026 (*Redress Compliance*) montre que les trois grands cloud (SageMaker, Azure ML, Vertex AI) facturent le calcul de base à des taux proches, mais que l'écart de **20 à 50 %** provient des **majorations d'instances**, des **frais de services MLOps** et des **coûts de sortie de données** (egress).

| Coût caché | Impact | Exemple concret pour ObRail |
|------------|--------|------------------------------|
| **Idle endpoints** | Les endpoints d'inférence facturent à l'heure, même sans usage | Une API maintenue active 24/7 pour un usage académique représenterait un surcoût significatif |
| **Egress** | Transfert de données entre régions ou clouds | Si les données d'entraînement sont sur un cloud et l'inférence sur un autre, les frais de transfert peuvent annuler les avantages tarifaires |
| **Pénurie de GPU** | Indisponibilité des instances préférées | Les équipes sont poussées vers des instances plus grandes et plus chères |
| **Multiplicité des services** | Vertex AI facture chaque composant séparément | Un projet utilisant Vertex AI Pipelines, Feature Store et AutoML cumulerait plusieurs mètres de facturation |

**Recommandation** : Pour un projet académique comme ObRail, **HuggingFace AutoTrain** constitue une alternative intéressante (gratuit jusqu'à 10 modèles/mois), mais son explicabilité limitée le disqualifie pour la phase de production si les exigences de documentation sont strictes.

## Axe 2 — Veille Réglementaire

### 2.1 RGPD — Règlement Général sur la Protection des Données

**Contexte projet** : Le projet ObRail utilise des **données agrégées par pays** (42 pays × 15 ans), sans aucune donnée personnelle. La cible `en_declin` est construite à partir de données historiques réelles (`passengers`), sans règle arbitraire fondée sur des seuils (`phase_1_construction_dataset.md`). Les modèles `.joblib` sauvegardés ne contiennent pas de données brutes.

**Les quatre principes cardinaux du RGPD** : Le RGPD repose sur des principes fondamentaux qui guident la protection des données à caractère personnel. Ces principes sont :

1.  **Finalité** : les données doivent être collectées pour des finalités déterminées, explicites et légitimes, et ne pas être traitées ultérieurement de manière incompatible.
2.  **Minimisation** : les données doivent être adéquates, pertinentes et limitées à ce qui est nécessaire au regard des finalités pour lesquelles elles sont traitées.
3.  **Sécurité** : les données doivent être traitées de manière à garantir une sécurité appropriée, y compris la protection contre le traitement non autorisé ou illicite.
4.  **Transparence** : les personnes concernées doivent être informées de manière concise, transparente et compréhensible sur les traitements effectués.

**Application concrète dans le projet ObRail** :

| Principe RGPD | Application dans le projet | Justification |
|---------------|----------------------------|---------------|
| **Finalité** | Prévision de fréquentation et détection des pays en déclin | L'objectif est défini, explicite et légitime (conforme aux enjeux ObRail : *"Anticiper la demande en mobilité ferroviaire"* et *"Évaluer l'impact environnemental futur"*) |
| **Minimisation** | 6 variables numériques + pays (47 features après OHE). Seules les variables strictement nécessaires sont conservées. Par exemple, les données de `facts_night_trains` (15 538 trajets) ont été écartées car non pertinentes pour le sujet retenu. | Seules les données strictement nécessaires sont conservées ; les variables `passengers_lag1` et `passengers_lag2` sont indispensables pour capturer la dynamique temporelle |
| **Sécurité** | Modèles stockés localement ; aucun exposé public sans authentification. Les données sont en local, non versionnées sur Git. | Mesures adéquates au regard des risques (données agrégées, pas de données personnelles) |
| **Transparence** | SHAP, importance des variables, documentation complète (`rapport_evaluation.md`, notebooks d'explicabilité). Les prédictions de l'API retournent la probabilité associée. | Les décisions du modèle sont interprétables et justifiables auprès des institutions européennes |

**Recommandations CNIL** : La CNIL a publié un recommandation sur l'application du RGPD au développement des systèmes d'IA. La CNIL rappelle que les principes de finalité, minimisation, sécurité et transparence **s'appliquent pleinement**, même lorsque les données sont agrégées. Elle insiste sur la nécessité de **documenter les choix de conception** (ce qui a été fait via les phases de projet) et de **mettre en place des mesures techniques** pour garantir la sécurité.

**Exemple concret** : La CNIL donne l'exemple d'une organisation qui "a créé une base de données de photographies de wagons de train en service – c'est-à-dire avec des personnes présentes – afin d'entraîner un algorithme à mesurer le remplissage et l'occupation des trains en gare". ObRail, en utilisant des données **agrégées par pays et non des données individuelles**, se situe dans un cadre de risque bien plus faible et respecte pleinement le principe de minimisation.

### 2.2 AI Act — Règlement Européen sur l'Intelligence Artificielle

**Contexte projet** : Le modèle ObRail entre dans la catégorie des systèmes d'IA **à risque limité** : il n'entre pas dans les pratiques interdites (article 5), ne concerne pas la sécurité des personnes ni les infrastructures critiques, et constitue un outil d'aide à la décision sans effet contraignant.

**Article 5 — Pratiques interdites** : L'article 5 de l'AI Act interdit huit pratiques spécifiques jugées inacceptables. Ces pratiques incluent :

-   **Manipulation subliminale** : systèmes qui altèrent le comportement humain de manière subliminale ou trompeuse, causant un préjudice.
-   **Exploitation des vulnérabilités** : systèmes qui exploitent les vulnérabilités des personnes en raison de leur âge, handicap ou situation socio-économique.
-   **Notation sociale** : systèmes de notation sociale (crédit social) par les autorités publiques.
-   **Reconnaissance des émotions** : systèmes de reconnaissance des émotions sur le lieu de travail ou dans les établissements d'enseignement.
-   **Scraping facial** : collecte non ciblée de données biométriques à partir d'Internet ou de vidéosurveillance.
-   **Police prédictive** : systèmes de profilage pour évaluer le risque qu'une personne commette une infraction.
-   **Catégorisation biométrique** : systèmes qui catégorisent les personnes en fonction de leurs caractéristiques biométriques.

**Application à ObRail** : Le modèle développé pour ObRail **n'entre dans aucune de ces catégories** : il ne manipule pas le comportement humain, n'exploite aucune vulnérabilité, ne pratique aucune notation sociale, ne reconnaît pas d'émotions, ne collecte pas de données biométriques, ne fait pas de police prédictive et ne catégorise pas les personnes. Il s'agit d'un outil d'aide à la décision pour des institutions et opérateurs ferroviaires, basé sur des données agrégées par pays.

**Calendrier — Points critiques** :

| Date | Événement | Impact pour ObRail |
|------|-----------|-------------------|
| **2 août 2026** | Entrée en vigueur des obligations de transparence (article 50) | Tous les systèmes IA doivent informer les utilisateurs qu'ils interagissent avec une IA |
| **2 décembre 2026** | Report des obligations pour les fournisseurs (Digital Omnibus) | Délai supplémentaire pour s'adapter |
| **Décembre 2025** | Code de pratique sur le marquage des contenus générés par IA | Anticiper les exigences de traçabilité |

**Sanctions** : Le non-respect de l'article 50 peut entraîner des amendes allant jusqu'à **15 millions d'euros** ou **3 % du chiffre d'affaires annuel mondial**.

**Application à ObRail** :
-   Les prédictions de l'API FastAPI (`/predict/classification` et `/predict/regression`) doivent **informer l'utilisateur** qu'elles sont générées par une IA.
-   Les **limites et biais** du modèle (documentés dans `rapport_evaluation.md`) doivent être communiqués aux utilisateurs.
-   La **notice de conformité** doit être préparée pour la soutenance.

### 2.3 Synthèse des risques réglementaires

| Risque | Probabilité | Impact | Mesure corrective | Échéance |
|--------|-------------|--------|-------------------|----------|
| Non-conformité RGPD | Faible | Élevé | Audit des données ; documentation | Avant livraison |
| Reclassification AI Act | Faible | Moyen | Suivi des évolutions ; notice de conformité | 2 août 2026 |
| Évolution des seuils de risque | Moyenne | Moyen | Veille réglementaire continue | Permanent |

## Axe 3 — Veille Sécurité

### 3.1 Vulnérabilités des modèles de Machine Learning

**Contexte projet** : Les modèles ObRail sont entraînés sur des données agrégées par pays, avec des **features numériques standardisées** et une **variable catégorielle** (pays encodée en One-Hot). Le risque d'attaque est **très faible** car les données sont publiques et agrégées, mais la veille est nécessaire pour anticiper d'éventuelles évolutions.

**État de l'art** :

**Adversarial Machine Learning** : Une étude de mars 2026 (*Array*) a benchmarké la résilience adversarial de sept modèles ML pour la détection DDoS. Les résultats montrent que :
-   Les modèles **boosting** (XGBoost, LightGBM) présentent **la plus haute résilience** sous stress adversarial.
-   Les modèles comme la **Régression Logistique** et le **MLP** subissent une **dégradation significative** des performances, même après entraînement adversarial.
-   L'**entraînement adversarial** (augmentation du dataset avec des échantillons perturbés) améliore substantiellement la robustesse de tous les modèles.

**Application à ObRail** :

| Type d'attaque | Risque pour ObRail | Justification |
|----------------|-------------------|---------------|
| **Data poisoning** | Très faible | Données agrégées par pays, difficile à contaminer |
| **Evasion** | Très faible | Données publiques et agrégées ; pas d'incitation à tromper le modèle |
| **Model stealing** | Faible | API exposée localement uniquement ; pas de valeur commerciale directe |

**Recommandation** : Bien que le risque soit faible, l'**entraînement adversarial** pourrait être exploré dans une version future pour renforcer la robustesse du modèle XGBoost.

### 3.2 Sécurité des données et de l'infrastructure

**Contexte projet** : Les données d'entraînement sont stockées dans `data/ml/` sous forme de CSV, les modèles dans `ia/models/` sous forme `.joblib`, et l'API FastAPI est exposée localement.

**Bonnes pratiques CNIL** : La CNIL a publié une fiche pratique sur la **sécurité du développement des systèmes d'IA**. Les mesures recommandées incluent :

| Mesure | Application à ObRail | Statut |
|--------|----------------------|--------|
| Chiffrement des données | Données CSV en local, non versionnées | ✅ |
| Contrôle d'accès | Restreint à l'équipe projet | ✅ |
| Journalisation | Scripts versionnés ; métriques sauvegardées en JSON | ✅ |
| Anonymisation | Données agrégées par pays — pas d'identification individuelle | ✅ |

**NIST Cyber AI Profile** : En janvier 2026, le NIST a organisé un atelier sur le **Cyber AI Profile**, visant à aider les organisations à adopter l'IA tout en gérant les risques cyber. Le draft, ouvert aux commentaires publics jusqu'au 30 janvier 2026, pose des questions clés : *"Si un système IA échoue ou est compromis, savons-nous comment réagir et récupérer ?"*.

**Application à ObRail** :
-   Les **modèles `.joblib`** sont les artefacts critiques à protéger.
-   L'**API FastAPI** devra intégrer une **authentification** avant une mise en production.

### 3.3 Synthèse des risques de sécurité

| Risque | Probabilité | Impact | Mesure corrective | Priorité |
|--------|-------------|--------|-------------------|----------|
| Accès non autorisé aux modèles | Faible | Élevé | Authentification sur l'API | Haute |
| Data drift | Moyenne | Moyen | Monitoring des entrées en production | Moyenne |
| Attaque adversarial | Très faible | Faible | Entraînement adversarial (optionnel) | Basse |

## Synthèse des Recommandations

### Court terme (avant livraison)

| Axe | Recommandation | Justification |
|-----|----------------|---------------|
| Algorithmique | Documenter les limites du split aléatoire et proposer un split temporel (`GroupShuffleSplit` par pays) | Améliorer la rigueur de l'évaluation |
| Réglementaire | Rédiger la notice de conformité RGPD et AI Act | Exigence du cahier des charges |
| Sécurité | Vérifier l'absence de données personnelles dans les artefacts | Conformité RGPD |

### Moyen terme (phase de production)

| Axe | Recommandation | Justification |
|-----|----------------|---------------|
| Algorithmique | Explorer les modèles hybrides Ridge-XGBoost ; enrichir les données avec des indicateurs macroéconomiques | Améliorer la robustesse sur les petits pays |
| Réglementaire | Mettre en place une veille réglementaire continue (AI Act, CNIL) | Suivre les évolutions normatives |
| Sécurité | Auditer la robustesse des modèles ; implémenter le monitoring des entrées | Prévenir la dégradation des performances |

## Sources de la veille

1.  **CNIL**. (2026, 5 janvier). *AI system development: CNIL's recommendations to comply with the GDPR*. https://www.cnil.fr/fr/node/167989
2.  **Commission Européenne**. (2024). *Règlement sur l'IA (UE) 2024/1689 (AI Act)*.
3.  **William Fry**. (2026, 11 juin). *Part 1: AI Act Articles 50(1) and 50(2) Transparency Obligations*. https://www.williamfry.com/knowledge/part-1-ai-act-articles-501-and-502-transparency-obligations/
4.  **Achterberg, J. et al.** (2026, 6 mars). *XGenBoost: Synthesizing Small and Large Tabular Datasets with XGBoost*. arXiv:2603.06904. https://arxiv.org/abs/2603.06904
5.  **Redress Compliance**. (2026, 2 avril). *SageMaker vs Azure ML vs Vertex AI: The 2026 Cost Comparison*. https://redresscompliance.com/aws-sagemaker-vs-azure-ml-vs-vertex-ai-comparison
6.  **Array Journal**. (2026, mars). *Benchmarking the adversarial resilience of machine learning models for DDoS detection*. Vol. 29, 100664. https://www.sciencedirect.com/science/article/pii/S2590005625002917
7.  **Nature Scientific Reports**. (2026, janvier). *Table 3: XGBoost performance (10-fold CV)*. https://www.nature.com/
8.  **NIST NCCoE**. (2026, janvier). *Cyber AI Profile Preliminary Draft*. https://www.nist.gov
9.  **Applied Soft Computing**. (2026, 18 mai). *Hybrid Ensemble Learning Framework Integrating a Time-Varying Decomposition Method*. https://www.sciencedirect.com/
10. **Travers Smith**. (2026, 27 mai). *The EU AI Act – the current state of play*. https://www.traverssmith.com/
11. **CNIL**. (2026). *Ensuring the security of an AI system's development* (How-to sheet). https://www.cnil.fr/