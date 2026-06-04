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
### Ce que fait ce simulateur

- **Page 1 — Bilan matière** : visualise ce que produit la raffinerie pour chaque brut
- **Page 2 — Optimiseur** : trouve le mix de bruts qui maximise la marge

### Comment naviguer
Utilise le menu à gauche pour changer de page.
""")
