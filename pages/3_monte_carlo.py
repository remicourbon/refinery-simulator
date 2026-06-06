# pages/3_monte_carlo.py
import streamlit as st
import plotly.express as px
import pandas as pd
from refinery.monte_carlo import simuler_monte_carlo
from refinery.optimizer import optimiser_mix
from refinery.sidebar import render_sidebar

st.title("🎲 Simulation Monte Carlo")
st.caption("Distribution des marges et VaR 95%")

config = render_sidebar()

with st.sidebar:
    st.divider()
    st.header("Paramètres")
    n_simulations = st.slider("Nombre de scénarios", 100, 2000, 1000, 100)

st.info(f"Configuration active : **{config.name}** — CDU {config.cdu_capacity_kbd} kbd")

st.divider()

st.markdown("""
**Comment ça marche ?**
- On calcule le mix optimal avec la configuration active
- On simule N scénarios où les prix varient aléatoirement
- La VaR 95% = seuil dépassé dans 95% des scénarios
""")

st.divider()

if st.button("🚀 Lancer la simulation"):

    with st.spinner(f"Calcul de {n_simulations} scénarios..."):
        resultat_opt = optimiser_mix(config=config)
        mix = resultat_opt["mix"]
        resultats = simuler_monte_carlo(mix, config=config, n_simulations=n_simulations)

    col1, col2, col3 = st.columns(3)
    col1.metric("MBR moyenne", f"{resultats['moyenne']} $/bbl")
    col2.metric("VaR 95%", f"{resultats['var_95']} $/bbl")
    col3.metric("Prob. marge négative", f"{resultats['prob_negative']} %")

    st.divider()

    df = pd.DataFrame({"MBR simulée ($/bbl)": resultats["mbrs"]})
    fig = px.histogram(
        df,
        x="MBR simulée ($/bbl)",
        nbins=50,
        title=f"Distribution des marges — {n_simulations} scénarios — {config.name}",
        color_discrete_sequence=["#2ecc71"]
    )
    fig.add_vline(
        x=resultats["var_95"],
        line_dash="dash",
        line_color="red",
        annotation_text=f"VaR 95% : {resultats['var_95']} $/bbl"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    **Lecture :**
    - Ligne rouge = VaR 95% à **{resultats['var_95']} $/bbl**
    - Probabilité de marge négative : **{resultats['prob_negative']}%**
    """)
    