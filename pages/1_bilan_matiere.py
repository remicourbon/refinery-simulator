# pages/1_bilan_matiere.py
import streamlit as st
import plotly.express as px
import pandas as pd
from data.crudes import CRUDES
from refinery.balance import run_balance
from refinery.sidebar import render_sidebar

st.title("📊 Bilan matière")
st.caption("Ce que produit la raffinerie selon le brut et la configuration choisie")

config = render_sidebar()

with st.sidebar:
    st.divider()
    st.header("Brut")
    choix_brut = st.selectbox("Brut", options=list(CRUDES.keys()))

crude = CRUDES[choix_brut]
df = run_balance(crude, config=config)

st.subheader(f"{config.name} — {choix_brut}")

col1, col2, col3 = st.columns(3)
col1.metric("CDU", f"{config.cdu_capacity_kbd} kbd")
col2.metric("Soufre brut", f"{crude.sulfur_pct}%")
col3.metric("Prix brut", f"{crude.price_usd_bbl} $/bbl")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Configuration des unités")

    unites = [
        {"Unité": "CDU",   "kbd": config.cdu_capacity_kbd, "Active": "✅"},
        {"Unité": "VDU",   "kbd": config.vdu_capacity_kbd   if config.vdu_active   else 0, "Active": "✅" if config.vdu_active   else "❌"},
        {"Unité": "FCCU",  "kbd": config.fccu_capacity_kbd  if config.fccu_active  else 0, "Active": "✅" if config.fccu_active  else "❌"},
        {"Unité": "HCU",   "kbd": config.hcu_capacity_kbd   if config.hcu_active   else 0, "Active": "✅" if config.hcu_active   else "❌"},
        {"Unité": "Coker", "kbd": config.coker_capacity_kbd if config.coker_active else 0, "Active": "✅" if config.coker_active else "❌"},
    ]

    df_unites = pd.DataFrame(unites).set_index("Unité")
    st.dataframe(df_unites, use_container_width=True)

with col_right:
    st.subheader("Mass balance")

    df_display = df[["%mt", "%vol", "kbd"]].copy()

    total = pd.DataFrame([{
        "%mt":  round(df_display["%mt"].sum(), 1),
        "%vol": round(df_display["%vol"].sum(), 1),
        "kbd":  round(df_display["kbd"].sum(), 2),
    }], index=["Total"])

    df_display = pd.concat([df_display, total])
    st.dataframe(df_display, use_container_width=True)

st.divider()

st.subheader("Répartition en %mt")
fig = px.bar(
    df.reset_index(),
    x="Produit",
    y="%mt",
    color="Produit",
    title=f"{config.name} — {choix_brut}",
)
st.plotly_chart(fig, use_container_width=True)
