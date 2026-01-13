# POC Technique - SystemX / Projet SYNERGIES

## Contexte
Ce démonstrateur technique a été réalisé dans le cadre de l'entretien pour le stage **"Génération de données pour la validation de systèmes de conduite automatisée"**.

Il simule une chaîne de traitement simplifiée (ETL) telle que décrite dans l'offre :
1. **Simulation** : Génération de données de télémétrie véhicule (mocking de SCANeR/Carla).
2. **Analyse** : Calcul d'indicateurs de criticité (Time To Collision - TTC).
3. **Extraction** : Conversion des scénarios critiques vers un format standardisé JSON (concept SYNERGIES-SSD).

## Architecture
Le projet est codé en **Python pur** (Standard Library) pour garantir la portabilité et la facilité d'exécution.

```text
.
├── pipeline.py        # Orchestrateur principal
├── data/              # Dossier des I/O (CSV bruts et JSON finaux)
└── src/
    ├── generator.py   # Simule le capteur radar/lidar et la physique du véhicule
    ├── analyzer.py    # Détecte les anomalies (TTC < seuil)
    └── adapter.py     # Formate les données pour l'interopérabilité
```

## Comment exécuter
```bash
python pipeline.py
```

## Visualisation (Bonus)
Une interface graphique interactive a été développée pour visualiser les données et ajuster les seuils en temps réel.

1. Installation des dépendances :
```bash
pip install -r requirements.txt
```

2. Lancement du Dashboard :
```bash
streamlit run dashboard.py
```

## Qualité & Tests (CI/CD)
Le projet intègre une suite de tests unitaires pour valider la logique métier (notamment le calcul critique du TTC et les cas limites).

Pour lancer les tests :
```bash
python -m unittest discover tests
```

## Détails Techniques
- **Calcul du TTC** : $TTC = \frac{Distance}{VitesseRelative}$. Si $TTC < 2.5s$, l'événement est marqué comme critique.
- **Gestion des erreurs** : Prise en compte de la division par zéro (véhicule à l'arrêt).
- **Extensibilité** : L'architecture Orientée Objet permet d'ajouter facilement de nouveaux connecteurs (ex: un parser pour OpenSCENARIO).
