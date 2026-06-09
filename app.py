# app.py
import streamlit as st

st.set_page_config(
    page_title="Refinery Simulator",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛢️ Refinery Simulator")
st.caption("Simulateur de marge de raffinage — Brent, Urals, Arab Light, Sahara Blend")

st.divider()

st.markdown("""
### Ce que fait ce simulateur

Ce projet modélise le fonctionnement complet d'une raffinerie de pétrole —
du brut entrant jusqu'aux produits finis, avec optimisation de la marge et analyse du risque.

Il est construit sur un moteur de **bilan matière** réaliste :
5 unités de conversion (CDU, VDU, FCCU, HCU, Coker), des rendements
différenciés par brut, et des prix réels récupérés via l'API EIA.
""")

st.markdown("""
### Les 4 pages

| Page | Objectif |
|------|----------|
| 📊 **Bilan matière** | Rendements par produit selon le brut et la configuration |
| ⚙️ **Optimiseur** | Mix de bruts optimal sous contraintes soufre et volume |
| 🎲 **Monte Carlo** | Distribution des marges et VaR 95% sur 1000 scénarios |
| 📈 **Marges** | Évolution historique de la MBR et des crack spreads EIA |
""")

st.divider()

st.markdown("""
### Comment utiliser

1. **Configure ta raffinerie** dans la sidebar — choisis une config prédéfinie (Dangote...) ou personnalise chaque unité
2. **Choisis ton brut ou ton mix** — un seul brut ou un mix pondéré des 4 bruts
3. **Explore les pages** — le bilan matière se met à jour en temps réel, l'optimiseur et le Monte Carlo se lancent sur bouton
""")

st.divider()


st.markdown("""
### Stack technique

`Python` · `Streamlit` · `scipy` (optimisation) · `pandas` · `plotly` · `API EIA` (prix réels)
""")

st.caption("Remi Courbon — 2026 · [GitHub](https://github.com/remicourbon/refinery-simulator)")

