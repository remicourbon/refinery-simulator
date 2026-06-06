# pages/2_optimiseur.py
import streamlit as st
import plotly.express as px
from refinery.optimizer import optimiser_mix, calcul_soufre_mix
from refinery.sidebar import render_sidebar
from data.crudes import CRUDES

st.title("⚙️ Optimiseur de mix brut")
st.caption("Trouve le mix de bruts qui maximise la marge de raffinage")

config = render_sidebar()

with st.sidebar:
    st.divider()
    st.header("Contraintes")

    st.subheader("Soufre")
    soufre_max = st.slider(
        "Soufre max du mix (%)",
        min_value=0.1,
        max_value=3.0,
        value=2.0,
        step=0.1,
        help="IMO 2020 = 0.5% | Standard = 2.0%"
    )

    st.subheader("Mix")
    mix_min = st.slider(
        "Part minimale par brut (%)",
        min_value=0,
        max_value=30,
        value=10,
        step=5,
        help="Chaque brut doit représenter au moins X% du mix"
    )
    mix_max = st.slider(
        "Part maximale par brut (%)",
        min_value=30,
        max_value=100,
        value=60,
        step=5,
        help="Aucun brut ne peut dépasser X% du mix"
    )

st.info(f"Configuration active : **{config.name}** — CDU {config.cdu_capacity_kbd} kbd")

st.divider()

st.subheader("Contraintes actives")
col1, col2, col3 = st.columns(3)
col1.metric("Soufre max", f"{soufre_max} %")
col2.metric("Part min par brut", f"{mix_min} %")
col3.metric("Part max par brut", f"{mix_max} %")

st.divider()

if st.button("🚀 Lancer l'optimisation"):

    with st.spinner("Calcul en cours..."):
        resultat = optimiser_mix(
            config=config,
            soufre_max=soufre_max,
            mix_min=max(mix_min / 100, 0.01),
            mix_max=mix_max / 100,
        )

    mix = resultat["mix"]
    mbr = resultat["mbr"]

    col1, col2, col3 = st.columns(3)
    col1.metric("MBR optimale", f"{mbr} $/bbl")
    col2.metric("Soufre mix", f"{resultat['soufre']} %")
    col3.metric("Configuration", config.name)

    st.divider()

    st.subheader("Composition du mix optimal")
    for nom, fraction in mix.items():
        if fraction > 0.01:
            prix   = CRUDES[nom].price_usd_bbl
            soufre = CRUDES[nom].sulfur_pct
            st.write(f"**{nom}** : {round(fraction * 100, 1)}% — {prix} $/bbl — {soufre}% S")

    st.divider()

    mix_filtre = {k: v for k, v in mix.items() if v > 0.01}
    fig = px.pie(
        values=list(mix_filtre.values()),
        names=list(mix_filtre.keys()),
        title=f"Mix optimal — {config.name} — Soufre max {soufre_max}%",
    )
    st.plotly_chart(fig, use_container_width=True)

    