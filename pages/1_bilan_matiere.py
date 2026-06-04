# pages/1_bilan_matiere.py
# Page 1 : bilan matière par brut

import streamlit as st
import plotly.express as px
from data.crudes import CRUDES
from refinery.balance import run_balance

st.title("📊 Bilan matière")
st.caption("Ce que produit la raffinerie selon le brut choisi")

# --- Sidebar : choix du brut et de la capacité ---
with st.sidebar:
    st.header("Paramètres")
    
    choix_brut = st.selectbox(
        "Brut",
        options=list(CRUDES.keys())
    )
    
    capacite = st.slider(
        "Capacité CDU (kbd)",
        min_value=50,
        max_value=300,
        value=100,
        step=10
    )

# --- Calcul ---
crude = CRUDES[choix_brut]
df = run_balance(crude, cdu_capacity_kbd=capacite)

# --- Affichage ---
st.subheader(f"Brut : {choix_brut} — {crude.api}° API — {crude.sulfur_pct}% soufre")

col1, col2, col3 = st.columns(3)
col1.metric("Capacité CDU", f"{capacite} kbd")
col2.metric("Densité", f"{crude.density} t/m³")
col3.metric("Prix", f"{crude.price_usd_bbl} $/bbl")

st.divider()

# --- Tableau ---
st.subheader("Rendements par produit")
st.dataframe(df, use_container_width=True)

st.divider()

# --- Graphique ---
st.subheader("Répartition en %mt")
fig = px.bar(
    df.reset_index(),
    x="Produit",
    y="%mt",
    color="Produit",
    title=f"Rendements {choix_brut} — {capacite} kbd",
)
st.plotly_chart(fig, use_container_width=True)