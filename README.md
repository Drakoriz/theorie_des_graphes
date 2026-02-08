# Théorie des Graphes - Application Interactive

Une application web streamlit pour visualiser et comprendre les algorithmes de graphes avec plusieurs features.

## Auteurs

**William WAN & Hsiao-Wen-Paul LO**

## Description

Cette application permet d'explorer de manière interactive les principaux algorithmes de la théorie des graphes à travers des visualisations animées, avec la possibilité de mettre sur pause. 

## Lancement de l'application

Dans le répertoire du projet, exécutez :

```bash
streamlit run main.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse `http://localhost:8501`

## Fonctionnalités

### Algorithmes Implémentés

#### Parcours de Graphes
- **BFS (Breadth-First Search)** - Parcours en largeur
- **DFS (Depth-First Search)** - Parcours en profondeur

#### Arbres Couvrants Minimums
- **Algorithme de Prim** - Construction incrémentale
- **Algorithme de Kruskal** - Tri des arêtes

#### Plus Courts Chemins
- **Dijkstra** - Chemins optimaux (poids positifs)
- **Bellman-Ford** - Détection de cycles négatifs
- **Floyd-Warshall** - Tous les plus courts chemins

#### Ordonnancement de Projet
- **Méthode PERT** - Gestion de projets avec dépendances
- **Diagrammes PERT et Gantt** - Visualisation temporelle

### Gestion des Données

- **Import/Export CSV** - Chargement de vos propres graphes
- **Éditeur interactif** - Modification en temps réel des arêtes
- **Génération aléatoire** - Création de graphes personnalisés
- **Validation automatique** - Vérification de la cohérence des données
- **Ajout personnel des tasks pour PERT** - Création de projets personnalisés 

### Visualisation

- **Animations pas à pas** - Suivi détaillé de l'exécution
- **Contrôles interactifs** - Pause, reprise, vitesse ajustable
- **Historique complet** - Revue de toutes les étapes
- **Graphiques colorés** - Distinction visuelle des états


## Utilisation

### Mode Algorithmes

1. Sélectionnez une **catégorie d'algorithme** dans la barre latérale
2. Choisissez l'**algorithme spécifique** et ses paramètres
3. Cliquez sur **Démarrer** pour lancer l'animation
4. Utilisez **Pause/Reprendre** pour contrôler l'exécution
5. Ajustez la **vitesse** avec le slider

### Mode Gestion des Données

1. Cliquez sur **Gestion des données** dans la navigation
2. Choisissez parmi 4 options :
   - **Télécharger** les données actuelles
   - **Importer** un fichier CSV personnalisé qui introduira les données de graphs,
   - **Modifier** les données avec l'éditeur pour tester certains algo, ajouter des arêtes négatives par exemple
   - **Générer** un graphe aléatoire si on veut peu de nœuds sans pour autant avoir des données derrières 

## Structure du Projet

```
theorie_des_graphes/
├── main.py                      # Application principale Streamlit
├── graphes_utils.py             # Fonctions utilitaires
├── graphes_parcours.py          # BFS et DFS
├── graphes_acpm.py              # Prim et Kruskal
├── graphes_short.py             # Dijkstra, Bellman-Ford, Floyd-Warshall
├── graphes_pert.py              # Méthode PERT
├── graphes_data_manager.py      # Gestion des données
├── style_loader.py              # Chargement CSS
├── styles.css                   # Styles personnalisés
├── villes.csv                   # Données par défaut
├── requirements.txt             # Dépendances Python
└── README.md                    # Ce fichier
```


