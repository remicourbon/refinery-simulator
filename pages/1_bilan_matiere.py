# pages/1_bilan_matiere.py
import streamlit as st
import plotly.express as px
from data.crudes import CRUDES
from refinery.config import CONFIGS, RefineryConfig
from refinery.balance import run_balance

st.title("📊 Bilan matière")
st.caption("Ce que produit la raffinerie selon le brut et la configuration choisie")

with st.sidebar:
    st.header("Brut")
    choix_brut = st.selectbox("Brut", options=list(CRUDES.keys()))

    st.divider()
    st.header("Configuration raffinerie")

    mode = st.radio("Mode", ["Prédéfinie", "Personnalisée"])

    if mode == "Prédéfinie":
        choix_config = st.selectbox("Raffinerie", options=list(CONFIGS.keys()))
        config = CONFIGS[choix_config]

    else:
        # L'utilisateur configure lui-même
        st.subheader("CDU — toujours active")
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
        )

# --- Calcul ---
crude = CRUDES[choix_brut]
df = run_balance(crude, config=config)

# --- Affichage ---
st.subheader(f"{config.name} — {choix_brut}")

col1, col2, col3 = st.columns(3)
col1.metric("CDU", f"{config.cdu_capacity_kbd} kbd")
col2.metric("Soufre brut", f"{crude.sulfur_pct}%")
col3.metric("Prix brut", f"{crude.price_usd_bbl} $/bbl")

st.divider()

st.subheader("Rendements par produit")
st.dataframe(df, use_container_width=True)

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