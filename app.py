# app.py
# Point d'entrée du dashboard — page d'accueil

import streamlit as st

st.set_page_config(
    page_title="Refinery Simulator",
    page_icon="🛢️",
    layout="wide"
)

st.title("🛢️ Refinery Simulator")
st.caption("Simulateur de marge de raffinage — Brent, Urals, Arab Light, Sahara Blend")

st.divider()

st.markdown("""
### Bienvenue

Ce simulateur modélise le fonctionnement d'une raffinerie de pétrole —
du brut entrant jusqu'aux produits finis, en passant par l'optimisation de la marge.

### Les 4 pages

- **⚙️ Configuration** — choisis ta raffinerie et paramètre chaque unité
- **📊 Bilan matière** — visualise les rendements par produit selon le brut
- **🔧 Optimiseur** — trouve le mix de bruts qui maximise la marge (MBR)
- **🎲 Monte Carlo** — simule 1000 scénarios de prix et mesure le risque (VaR 95%)

### Comment utiliser

1. Commence par la page **Configuration** pour définir ta raffinerie
2. Explore le **Bilan matière** pour comprendre les rendements
3. Lance l'**Optimiseur** pour trouver le meilleur mix de bruts
4. Simule le **risque** avec le Monte Carlo

""")

st.divider()
st.caption("Projet Python — Remi Courbon — 2025")