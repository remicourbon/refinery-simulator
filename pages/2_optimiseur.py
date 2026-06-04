# pages/2_optimiseur.py
# Page 2 : optimiseur de mix brut

import streamlit as st
import plotly.express as px
from refinery.optimizer import optimiser_mix, calcul_mbr, PRODUCT_PRICES
from data.crudes import CRUDES

st.title("⚙️ Optimiseur de mix brut")
st.caption("Trouve le mix de bruts qui maximise la marge de raffinage")

# --- Sidebar ---
with st.sidebar:
    st.header("Paramètres")
    capacite = st.slider(
        "Capacité CDU (kbd)",
        min_value=50,
        max_value=300,
        value=100,
        step=10
    )

st.divider()

# --- Bouton de lancement ---
if st.button("🚀 Lancer l'optimisation"):

    with st.spinner("Calcul en cours..."):
        resultat = optimiser_mix(capacite_kbd=capacite)

    mix = resultat["mix"]
    mbr = resultat["mbr"]

    # --- Résultat principal ---
    st.subheader("Résultat")
    st.metric("MBR optimale", f"{mbr} $/bbl")

    st.divider()

    # --- Mix optimal ---
    st.subheader("Composition du mix optimal")
    for nom, fraction in mix.items():
        if fraction > 0.01:
            prix = CRUDES[nom].price_usd_bbl
            st.write(f"**{nom}** : {round(fraction * 100, 1)}% — {prix} $/bbl")

    st.divider()

    # --- Graphique camembert ---
    mix_filtre = {k: v for k, v in mix.items() if v > 0.01}
    fig = px.pie(
        values=list(mix_filtre.values()),
        names=list(mix_filtre.keys()),
        title="Mix optimal"
    )
    st.plotly_chart(fig, use_container_width=True)
    