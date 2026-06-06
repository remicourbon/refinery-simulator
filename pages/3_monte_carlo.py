# pages/3_monte_carlo.py
# Page 3 : simulation Monte Carlo

import streamlit as st
import plotly.express as px
import pandas as pd
from refinery.monte_carlo import simuler_monte_carlo
from refinery.optimizer import optimiser_mix
from refinery.config import CONFIGS, RefineryConfig

st.title("🎲 Simulation Monte Carlo")
st.caption("1000 scénarios de prix — distribution des marges et VaR 95%")

with st.sidebar:
    st.header("Configuration raffinerie")

    mode = st.radio("Mode", ["Prédéfinie", "Personnalisée"])

    if mode == "Prédéfinie":
        choix_config = st.selectbox("Raffinerie", options=list(CONFIGS.keys()))
        config = CONFIGS[choix_config]
    else:
        st.subheader("CDU")
        cdu_kbd = st.slider("CDU (kbd)", 50, 700, 100, 10)

        st.subheader("VDU")
        vdu_active = st.toggle("VDU active", value=True)
        vdu_kbd = st.slider("VDU (kbd)", 50, 700, 100, 10) if vdu_active else 0

        st.subheader("FCCU")
        fccu_active = st.toggle("FCCU active", value=True)
        fccu_kbd = st.slider("FCCU (kbd)", 10, 300, 50, 10) if fccu_active else 0

        st.subheader("HCU")
        hcu_active = st.toggle("HCU active", value=True)
        hcu_kbd = st.slider("HCU (kbd)", 10, 300, 50, 10) if hcu_active else 0

        st.subheader("Coker")
        coker_active = st.toggle("Coker active", value=True)
        coker_kbd = st.slider("Coker (kbd)", 10, 200, 40, 10) if coker_active else 0

        config = RefineryConfig(
            name="Personnalisée",
            cdu_capacity_kbd=cdu_kbd,
            vdu_active=vdu_active,
            vdu_capacity_kbd=vdu_kbd,
            fccu_active=fccu_active,
            fccu_capacity_kbd=fccu_kbd,
            hcu_active=hcu_active,
            hcu_capacity_kbd=hcu_kbd,
            coker_active=coker_active,
            coker_capacity_kbd=coker_kbd,
        )

    st.divider()
    n_simulations = st.slider("Nombre de scénarios", 100, 2000, 1000, 100)

st.divider()

st.markdown("""
**Comment ça marche ?**
- On calcule d'abord le mix optimal avec la configuration choisie
- On simule N scénarios où les prix des bruts (±15%) et des produits (±10%) varient
- On calcule la MBR pour chaque scénario
- La VaR 95% = dans 95% des scénarios, la marge dépasse ce seuil
""")

st.divider()

if st.button("🚀 Lancer la simulation"):

    with st.spinner(f"Calcul de {n_simulations} scénarios..."):
        resultat_opt = optimiser_mix(config=config)
        mix = resultat_opt["mix"]
        resultats = simuler_monte_carlo(mix, config=config, n_simulations=n_simulations)

    # Métriques
    col1, col2, col3 = st.columns(3)
    col1.metric("MBR moyenne", f"{resultats['moyenne']} $/bbl")
    col2.metric("VaR 95%", f"{resultats['var_95']} $/bbl")
    col3.metric("Prob. marge négative", f"{resultats['prob_negative']} %")

    st.divider()

    # Graphique
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

    st.divider()

    st.markdown(f"""
    **Lecture du graphique :**
    - Ligne rouge = VaR 95% à **{resultats['var_95']} $/bbl**
    - Dans 95% des scénarios, la marge dépasse ce seuil
    - Probabilité de marge négative : **{resultats['prob_negative']}%**
    - Configuration : **{config.name}**
    """)

    