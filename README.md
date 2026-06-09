# 🛢️ Refinery Simulator

Simulateur de marge de raffinage construit en Python et Streamlit.
Modélise le fonctionnement complet d'une raffinerie — du brut entrant jusqu'aux produits finis — avec optimisation de la marge et analyse du risque.

**[👉 Demo en ligne](https://refinery-simulator-testsimulation.streamlit.app)**

---

## Ce que fait ce projet

- **Bilan matière** : calcule les rendements par produit (LPG, Naphtha, Kérosène, Gazole, Diesel, Essence, HSFO, Pet_coke) selon le brut et la configuration de la raffinerie
- **Optimiseur de mix** : trouve le mix de bruts qui maximise la marge brute de raffinage (MBR) sous contraintes de soufre et de volume, via `scipy.optimize`
- **Monte Carlo** : simule 1000 scénarios de volatilité des prix et calcule la VaR 95%
- **Évolution des marges** : affiche l'historique de la MBR et des crack spreads avec les prix réels de l'API EIA

---

## Stack technique

| Outil | Usage |
|-------|-------|
| `Python 3.13` | Langage principal |
| `Streamlit` | Dashboard multi-pages |
| `scipy` | Optimisation du mix brut (SLSQP) |
| `pandas` | Calcul du bilan matière |
| `plotly` | Graphiques interactifs |
| `API EIA` | Prix réels Brent, Diesel, Kerosene |
| `numpy` | Simulation Monte Carlo |

---

## Structure du projet

```
refinery-simulator/
│
├── data/
│   ├── crudes.py        # Propriétés et yields des 4 bruts
│   └── prices.py        # Prix réels via API EIA
│
├── refinery/
│   ├── units.py         # CDU, VDU, FCCU, HCU, Coker
│   ├── balance.py       # Moteur de bilan matière (pattern pool)
│   ├── config.py        # Configuration des raffineries (Défaut, Dangote...)
│   ├── optimizer.py     # Optimiseur MBR + contrainte soufre
│   ├── monte_carlo.py   # Simulation Monte Carlo + VaR 95%
│   └── sidebar.py       # Sidebar partagée entre toutes les pages
│
├── pages/
│   ├── 1_bilan_matiere.py
│   ├── 2_optimiseur.py
│   ├── 3_monte_carlo.py
│   └── 4_marges.py
│
├── app.py               # Page d'accueil Streamlit
└── requirements.txt
```

---

## Les 4 bruts modélisés

| Brut | API | Soufre | Prix référence |
|------|-----|--------|----------------|
| Brent | 38.3° | 0.35% | spot EIA |
| Urals | 31.1° | 1.35% | Brent - 15$ |
| Arab Light | 32.8° | 1.80% | Brent - 4$ |
| Sahara Blend | 43.5° | 0.10% | Brent + 3$ |

---

## Les 5 unités de conversion

```
Brut → CDU → VDU → FCCU ┐
                  → HCU  ├→ Produits finis
                  → Coker┘
```

Chaque unité peut être activée/désactivée et sa capacité (kbd) est paramétrable.
Les flux non valorisés sont automatiquement orientés vers le HSFO (pattern pool).

---

## Installation

```bash
git clone https://github.com/remicourbon/refinery-simulator
cd refinery-simulator
pip install -r requirements.txt
```

Crée un fichier `.env` à la racine :

```
API_KEY_EIA=ta_clé_eia
```

Lance l'application :

```bash
streamlit run app.py
```

---

## Déploiement Streamlit Cloud

1. Fork ou clone ce repo sur GitHub
2. Va sur [share.streamlit.io](https://share.streamlit.io) et connecte ton repo
3. Dans **Settings → Secrets**, ajoute :

```toml
API_KEY_EIA = "ta_clé_eia"
```

Obtiens une clé gratuite sur [eia.gov/opendata](https://www.eia.gov/opendata).

---

## Auteur

**Remi Courbon** — 2026

Projet construit de zéro en Python dans le cadre d'un apprentissage autonome du trading pétrolier et de la modélisation de raffineries.
