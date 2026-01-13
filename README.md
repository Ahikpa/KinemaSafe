# KinemaSafe 🚗⚡
### Pipeline de Validation de Sécurité pour Systèmes Autonomes

**KinemaSafe** est une chaîne de traitement de données (ETL) conçue pour l'analyse et la qualification de scénarios critiques dans le domaine de la conduite automatisée (AD) et des systèmes d'aide à la conduite (ADAS).

## 🎯 Problématique
Les campagnes de simulation numérique génèrent des téraoctets de données de télémétrie. Cependant, 99% de ces données représentent des situations de conduite nominale (sans danger).
**L'objectif de KinemaSafe** est d'automatiser le filtrage de ces données pour extraire uniquement les **"Near Misses"** (presque-accidents) et les convertir en indicateurs de sécurité exploitables.

## 🚀 Fonctionnalités
1. **Ingestion (ETL)** : Traitement de flux de télémétrie bruts (simulant des sorties LiDAR/Radar/CAN).
2. **Analyse Cinématique** : Calcul temps-réel du **TTC (Time-To-Collision)** et détection d'anomalies basée sur la physique.
3. **Standardisation** : Export des scénarios critiques vers un format JSON structuré et interopérable (prêt pour bases de données de validation).
4. **Visualisation** : Dashboard interactif pour l'analyse post-mortem des incidents.

## 🛠 Architecture Technique
Le projet est conçu en **Python** avec une architecture modulaire orientée objet, garantissant maintenabilité et extensibilité.

```text
.
├── pipeline.py        # Orchestrateur principal du workflow
├── data/              # Entrepôt de données (Logs bruts & Exports qualifiés)
├── tests/             # Suite de tests unitaires (Validation logique)
└── src/
    ├── generator.py   # Moteur de simulation de télémétrie
    ├── analyzer.py    # Cœur algorithmique (Détection & KPIs)
    └── adapter.py     # Module d'export (Formatage Standardisé)
```

## 💻 Installation & Usage

### Pré-requis
```bash
pip install -r requirements.txt
```

### 1. Lancer le Pipeline ETL
Génère la simulation, analyse les risques et exporte les résultats.
```bash
python pipeline.py
```

### 2. Visualiser les Résultats (Dashboard)
Lance l'interface d'analyse interactive pour explorer les données et ajuster les seuils de sensibilité.
```bash
streamlit run dashboard.py
```

### 3. Exécuter les Tests de Qualité
Vérifie la robustesse mathématique des algorithmes (CI/CD ready).
```bash
python -m unittest discover tests
```

## 📊 Détails Algorithmiques
L'indicateur principal est le **Time To Collision (TTC)** :
$$TTC = \frac{Distance}{VitesseRelative}$$

*   **Seuil Dynamique :** Les événements où $TTC < 2.5s$ sont marqués comme CRITIQUES.
*   **Robustesse :** Gestion des cas limites (division par zéro, véhicule à l'arrêt) pour assurer la stabilité en production.

## 🌍 Cas d'Usage
Bien que configuré pour l'automobile, ce pipeline est adaptable à d'autres secteurs :
*   **Robotique Industrielle :** Détection de proximité dangereuse entre bras robotisés et opérateurs.
*   **Maintenance Prédictive :** Analyse de séries temporelles pour détecter des dérives capteurs avant la panne.
