## Phase 1 – Préparation et analyse exploratoire des données (EDA)

### Objectif

Cette phase a pour objectif de vérifier la qualité du dataset construit lors de la phase précédente et de s'assurer qu'il est exploitable pour l'entraînement des futurs modèles de Machine Learning.

Elle constitue une étape essentielle entre la construction du Data Warehouse et la phase de modélisation, en permettant d'identifier d'éventuelles anomalies susceptibles d'impacter les performances des algorithmes.

---

### Analyse du dataset

Le dataset généré lors de la phase de préparation a été chargé puis analysé afin de vérifier sa structure et sa qualité.

Les contrôles réalisés portent notamment sur :

* la présence et le type des différentes variables ;
* les statistiques descriptives des variables numériques ;
* la recherche de valeurs manquantes ;
* la détection d'éventuels doublons ;
* l'identification de valeurs aberrantes (outliers) ;
* la répartition des variables catégorielles (pays, opérateurs, catégories de distance et de durée) ;
* la distribution de la variable cible `candidate_substitution`.

Ces analyses permettent de confirmer que les données sont cohérentes avant leur utilisation par les modèles d'apprentissage automatique.

---

### Analyse exploratoire

Une analyse exploratoire a également été réalisée afin de mieux comprendre les caractéristiques du jeu de données.

Plusieurs visualisations ont été produites :

* histogrammes des distances, durées et vitesses moyennes ;
* boxplots pour détecter les valeurs extrêmes ;
* répartition des trains de jour et de nuit ;
* répartition des opérateurs et des pays ;
* distribution de la variable cible ;
* matrice de corrélation des variables numériques.

Cette étape permet d'identifier les principales tendances du dataset et de mettre en évidence les relations entre les différentes variables.

---

### Résultats

L'analyse montre que le dataset est globalement propre et cohérent.

Les principales observations sont les suivantes :

* aucune anomalie majeure n'a été détectée ;
* les variables présentent des distributions cohérentes avec les caractéristiques des trajets ferroviaires européens ;
* la variable cible est déséquilibrée, avec une majorité de lignes considérées comme candidates à la substitution, ce qui sera pris en compte lors de l'évaluation des modèles.

Le dataset est désormais prêt pour les étapes de prétraitement (encodage, normalisation et séparation des données), puis pour l'entraînement et la comparaison des différents modèles de Machine Learning.
