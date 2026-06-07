# pages/4_marges.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data.prices import get_historique_brent, get_prix_bruts
from refinery.optimizer import calcul_mbr, PRODUCT_PRICES
from refinery.sidebar import render_sidebar
from data.crudes import CRUDES

st.title("📈 Évolution des marges")
st.caption("Prix réels EIA — historique Brent et MBR reconstituée")

config = render_sidebar()

with st.sidebar:
    st.divider()
    st.header("Paramètres")
    jours = st.slider("Historique (jours)", 30, 365, 90, 30)
    mix_fixe = {
        "Brent":        0.10,
        "Urals":        0.60,
        "Arab Light":   0.20,
        "Sahara Blend": 0.10,
    }

st.divider()

with st.spinner("Récupération des prix EIA..."):
    df_brent = get_historique_brent(jours)
    prix_actuels = get_prix_bruts()

# --- Métriques prix actuels ---
st.subheader("Prix actuels")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Brent",        f"{prix_actuels['Brent']} $/bbl")
col2.metric("Urals",        f"{prix_actuels['Urals']} $/bbl",
            f"{prix_actuels['Urals'] - prix_actuels['Brent']:.1f} vs Brent")
col3.metric("Arab Light",   f"{prix_actuels['Arab Light']} $/bbl",
            f"{prix_actuels['Arab Light'] - prix_actuels['Brent']:.1f} vs Brent")
col4.metric("Sahara Blend", f"{prix_actuels['Sahara Blend']} $/bbl",
            f"{prix_actuels['Sahara Blend'] - prix_actuels['Brent']:.1f} vs Brent")

st.divider()

# --- Courbe historique Brent ---
st.subheader(f"Prix Brent — {jours} derniers jours")
fig_brent = px.line(
    df_brent,
    x="date",
    y="prix",
    title=f"Brent spot — {jours} jours",
    labels={"prix": "$/bbl", "date": "Date"},
    color_discrete_sequence=["#2ecc71"]
)
fig_brent.update_layout(hovermode="x unified")
st.plotly_chart(fig_brent, use_container_width=True)

st.divider()

# --- MBR reconstituée ---
st.subheader("MBR reconstituée sur la période")
st.caption("Mix fixe : Urals 60% / Arab Light 20% / Brent 10% / Sahara 10%")

mbrs = []
for _, row in df_brent.iterrows():
    brent = row["prix"]
    prix_bruts_jour = {
        "Brent":        brent,
        "Urals":        brent - 15.0,
        "Arab Light":   brent - 4.0,
        "Sahara Blend": brent + 3.0,
    }
    mbr = calcul_mbr(
        mix=mix_fixe,
        config=config,
        prix_bruts=prix_bruts_jour,
    )
    mbrs.append({"date": row["date"], "MBR": round(mbr, 2)})

df_mbr = pd.DataFrame(mbrs)

fig_mbr = go.Figure()
fig_mbr.add_trace(go.Scatter(
    x=df_mbr["date"],
    y=df_mbr["MBR"],
    mode="lines",
    name="MBR",
    line=dict(color="#3498db", width=2),
    fill="tozeroy",
    fillcolor="rgba(52, 152, 219, 0.1)"
))
fig_mbr.add_hline(
    y=0,
    line_dash="dash",
    line_color="red",
    annotation_text="Seuil rentabilité"
)
fig_mbr.update_layout(
    title="MBR reconstituée ($/bbl)",
    xaxis_title="Date",
    yaxis_title="$/bbl",
    hovermode="x unified"
)
st.plotly_chart(fig_mbr, use_container_width=True)

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("MBR moyenne", f"{df_mbr['MBR'].mean():.2f} $/bbl")
col2.metric("MBR max", f"{df_mbr['MBR'].max():.2f} $/bbl")
col3.metric("MBR min", f"{df_mbr['MBR'].min():.2f} $/bbl")
