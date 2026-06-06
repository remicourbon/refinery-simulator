# pages/2_optimiseur.py
# Page 2 : optimiseur de mix brut

import streamlit as st
import plotly.express as px
from refinery.optimizer import optimiser_mix, PRODUCT_PRICES
from refinery.config import CONFIGS, RefineryConfig
from data.crudes import CRUDES

st.title("⚙️ Optimiseur de mix brut")
st.caption("Trouve le mix de bruts qui maximise la marge de raffinage")

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

if st.button("🚀 Lancer l'optimisation"):

    with st.spinner("Calcul en cours..."):
        resultat = optimiser_mix(config=config)

    mix = resultat["mix"]
    mbr = resultat["mbr"]

    # Résultat principal
    st.subheader("Résultat")
    col1, col2 = st.columns(2)
    col1.metric("MBR optimale", f"{mbr} $/bbl")
    col2.metric("Configuration", config.name)

    st.divider()

    # Mix optimal
    st.subheader("Composition du mix optimal")
    for nom, fraction in mix.items():
        if fraction > 0.01:
            prix = CRUDES[nom].price_usd_bbl
            st.write(f"**{nom}** : {round(fraction * 100, 1)}% — {prix} $/bbl")

    st.divider()

    # Graphique
    mix_filtre = {k: v for k, v in mix.items() if v > 0.01}
    fig = px.pie(
        values=list(mix_filtre.values()),
        names=list(mix_filtre.keys()),
        title=f"Mix optimal — {config.name}",
    )
    st.plotly_chart(fig, use_container_width=True)

    