# pages/1_bilan_matiere.py
import streamlit as st
import plotly.express as px
import pandas as pd
from data.crudes import CRUDES
from refinery.balance import run_balance
from refinery.sidebar import render_sidebar, render_mix_sidebar

st.title("📊 Bilan matière")
st.caption("Ce que produit la raffinerie selon le brut et la configuration choisie")

config = render_sidebar()
mix    = render_mix_sidebar()

# Calcul du bilan matière pour chaque brut du mix
# puis moyenne pondérée par les fractions
rows_total = {}
for nom, fraction in mix.items():
    if fraction <= 0:
        continue
    crude = CRUDES[nom]
    df_crude = run_balance(crude, config=config)
    for produit, row in df_crude.iterrows():
        if produit not in rows_total:
            rows_total[produit] = {"%mt": 0, "%vol": 0, "kbd": 0}
        rows_total[produit]["%mt"]  += row["%mt"]  * fraction
        rows_total[produit]["%vol"] += row["%vol"] * fraction
        rows_total[produit]["kbd"]  += row["kbd"]  * fraction

df = pd.DataFrame(rows_total).T
df.index.name = "Produit"
df = df.round(1)

# Titre dynamique
if mix.get("Brent", 0) == 1.0:
    titre = "Brent — 100%"
elif mix.get("Urals", 0) == 1.0:
    titre = "Urals — 100%"
elif mix.get("Arab Light", 0) == 1.0:
    titre = "Arab Light — 100%"
elif mix.get("Sahara Blend", 0) == 1.0:
    titre = "Sahara Blend — 100%"
else:
    parts = [f"{nom} {round(f*100)}%" for nom, f in mix.items() if f > 0]
    titre = " / ".join(parts)

st.subheader(f"{config.name} — {titre}")

col1, col2 = st.columns(2)
col1.metric("CDU", f"{config.cdu_capacity_kbd} kbd")
col2.metric("Configuration", config.name)

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
    title=titre,
)
st.plotly_chart(fig, use_container_width=True)
