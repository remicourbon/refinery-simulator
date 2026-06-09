# pages/4_marges.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data.prices import (get_historique_brent, get_prix_bruts,
                         get_prix_produits_eia, get_historique_produit)
from refinery.optimizer import calcul_mbr
from refinery.sidebar import render_sidebar, render_mix_sidebar

st.title("📈 Évolution des marges")
st.caption("Prix réels EIA — historique Brent, crack spreads et MBR reconstituée")

config = render_sidebar()
mix    = render_mix_sidebar()

with st.sidebar:
    st.divider()
    st.header("Paramètres")
    jours = st.slider("Historique (jours)", 30, 365, 90, 30)

st.divider()

with st.spinner("Récupération des prix EIA..."):
    df_brent      = get_historique_brent(jours)
    prix_bruts    = get_prix_bruts()
    prix_produits = get_prix_produits_eia()
    df_diesel     = get_historique_produit("Diesel",   jours)
    df_kerosene   = get_historique_produit("Kerosene", jours)

# --- Prix actuels ---
st.subheader("Prix actuels")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Brent",        f"{prix_bruts['Brent']} $/bbl")
col2.metric("Urals",        f"{prix_bruts['Urals']} $/bbl",
            f"{round(prix_bruts['Urals'] - prix_bruts['Brent'], 1)} vs Brent")
col3.metric("Arab Light",   f"{prix_bruts['Arab Light']} $/bbl",
            f"{round(prix_bruts['Arab Light'] - prix_bruts['Brent'], 1)} vs Brent")
col4.metric("Sahara Blend", f"{prix_bruts['Sahara Blend']} $/bbl",
            f"{round(prix_bruts['Sahara Blend'] - prix_bruts['Brent'], 1)} vs Brent")

st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Diesel",   f"{prix_produits['Diesel']} $/bbl",
            f"{round(prix_produits['Diesel'] - prix_bruts['Brent'], 1)} crack")
col2.metric("Kerosene", f"{prix_produits['Kerosene']} $/bbl",
            f"{round(prix_produits['Kerosene'] - prix_bruts['Brent'], 1)} crack")
col3.metric("Gasoline", f"{prix_produits['Gasoline']} $/bbl",
            f"{round(prix_produits['Gasoline'] - prix_bruts['Brent'], 1)} crack")
col4.metric("HSFO",     f"{prix_produits['HSFO']} $/bbl",
            f"{round(prix_produits['HSFO'] - prix_bruts['Brent'], 1)} crack")

st.divider()

# --- Courbe Brent ---
st.subheader(f"Prix Brent — {jours} derniers jours")
fig_brent = px.line(
    df_brent, x="date", y="prix",
    labels={"prix": "$/bbl", "date": "Date"},
    color_discrete_sequence=["#f39c12"]
)
fig_brent.update_layout(hovermode="x unified")
st.plotly_chart(fig_brent, use_container_width=True)

st.divider()

# --- Crack spreads historiques ---
st.subheader("Crack spreads historiques — Diesel & Kerosene")

df_cracks = df_brent.rename(columns={"prix": "Brent"})
df_cracks = df_cracks.merge(
    df_diesel.rename(columns={"prix": "Diesel"}), on="date", how="left"
)
df_cracks = df_cracks.merge(
    df_kerosene.rename(columns={"prix": "Kerosene"}), on="date", how="left"
)
df_cracks["Diesel crack"]   = df_cracks["Diesel"]   - df_cracks["Brent"]
df_cracks["Kerosene crack"] = df_cracks["Kerosene"] - df_cracks["Brent"]

fig_crack = go.Figure()
fig_crack.add_trace(go.Scatter(
    x=df_cracks["date"], y=df_cracks["Diesel crack"],
    name="Diesel crack", line=dict(color="#3498db", width=2)
))
fig_crack.add_trace(go.Scatter(
    x=df_cracks["date"], y=df_cracks["Kerosene crack"],
    name="Kerosene crack", line=dict(color="#2ecc71", width=2)
))
fig_crack.add_hline(y=0, line_dash="dash", line_color="red")
fig_crack.update_layout(
    yaxis_title="$/bbl vs Brent",
    hovermode="x unified"
)
st.plotly_chart(fig_crack, use_container_width=True)

st.divider()

# --- MBR reconstituée ---
# Titre dynamique selon le mix choisi
parts = [f"{nom} {round(f*100)}%" for nom, f in mix.items() if f > 0]
titre_mix = " / ".join(parts)

st.subheader("MBR reconstituée sur la période")
st.caption(f"Mix : {titre_mix}")
st.caption("Prix produits : Diesel et Kerosene réels EIA, autres en différentiel fixe")

mbrs = []
for _, row in df_brent.iterrows():
    brent = row["prix"]
    prix_bruts_jour = {
        "Brent":        brent,
        "Urals":        brent - 15.0,
        "Arab Light":   brent -  4.0,
        "Sahara Blend": brent +  3.0,
    }
    prix_produits_jour = {
        "LPG":      brent - 10.0,
        "Naphtha":  brent -  8.0,
        "Kerosene": brent + 15.0,
        "Gasoil":   brent + 12.0,
        "Diesel":   brent + 18.0,
        "Gasoline": brent + 20.0,
        "HSFO":     brent - 15.0,
        "Pet_coke": brent - 55.0,
    }
    mbr = calcul_mbr(
        mix=mix,
        config=config,
        prix_bruts=prix_bruts_jour,
        prix_produits=prix_produits_jour,
    )
    mbrs.append({"date": row["date"], "MBR": round(mbr, 2)})

df_mbr = pd.DataFrame(mbrs)

fig_mbr = go.Figure()
fig_mbr.add_trace(go.Scatter(
    x=df_mbr["date"], y=df_mbr["MBR"],
    mode="lines", name="MBR",
    line=dict(color="#9b59b6", width=2),
    fill="tozeroy",
    fillcolor="rgba(155, 89, 182, 0.1)"
))
fig_mbr.add_hline(
    y=0, line_dash="dash", line_color="red",
    annotation_text="Seuil rentabilité"
)
fig_mbr.update_layout(
    yaxis_title="$/bbl",
    hovermode="x unified"
)
st.plotly_chart(fig_mbr, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("MBR moyenne", f"{df_mbr['MBR'].mean():.2f} $/bbl")
col2.metric("MBR max",     f"{df_mbr['MBR'].max():.2f} $/bbl")
col3.metric("MBR min",     f"{df_mbr['MBR'].min():.2f} $/bbl")

st.divider()
st.caption("⚠️ Prix indicatifs — Brent, Diesel et Kerosene via EIA. Autres produits estimés par différentiel fixe sur le Brent.")

