# pages/3_monte_carlo.py
# Page 3 : simulation Monte Carlo

import streamlit as st
import plotly.express as px
import pandas as pd
from refinery.monte_carlo import simuler_monte_carlo
from refinery.optimizer import optimiser_mix

st.title("🎲 Simulation Monte Carlo")
st.caption("1000 scénarios de prix — distribution des marges et VaR 95%")

st.divider()

st.markdown("""
**Comment ça marche ?**
- On prend le mix optimal calculé par l'optimiseur
- On simule 1000 scénarios où les prix des bruts et des produits varient aléatoirement
- On calcule la marge pour chaque scénario
- On affiche la distribution et la VaR 95%
""")

st.divider()

if st.button("🚀 Lancer la simulation"):

    with st.spinner("Calcul de 1000 scénarios en cours..."):

        # On récupère le mix optimal
        resultat_opt = optimiser_mix(capacite_kbd=100)
        mix = resultat_opt["mix"]

        # On lance le Monte Carlo
        resultats = simuler_monte_carlo(mix, n_simulations=1000)

    # --- Métriques principales ---
    col1, col2, col3 = st.columns(3)
    col1.metric("MBR moyenne", f"{resultats['moyenne']} $/bbl")
    col2.metric("VaR 95%", f"{resultats['var_95']} $/bbl")
    col3.metric("Probabilité marge négative", f"{resultats['prob_negative']} %")

    st.divider()

    # --- Graphique distribution ---
    df = pd.DataFrame({"MBR simulée ($/bbl)": resultats["mbrs"]})

    fig = px.histogram(
        df,
        x="MBR simulée ($/bbl)",
        nbins=50,
        title="Distribution des marges — 1000 scénarios",
        color_discrete_sequence=["#2ecc71"]
    )

    fig.add_vline(
        x=resultats["var_95"],
        line_dash="dash",
        line_color="red",
        annotation_text=f"VaR 95% : {resultats['var_95']} $/bbl"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Explication ---
    st.markdown(f"""
    **Comment lire ce graphique :**
    - Chaque barre = un groupe de scénarios avec une MBR similaire
    - La **ligne rouge** = VaR 95% à **{resultats['var_95']} $/bbl**
    - Dans 95% des scénarios, ta marge dépasse ce seuil
    - Probabilité de marge négative : **{resultats['prob_negative']}%**
    """)