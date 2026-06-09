# refinery/sidebar.py
import streamlit as st
from refinery.config import CONFIGS, RefineryConfig


def _init_session_state():
    defaults = {
        "mode_config":  "Prédéfinie",
        "choix_config": "Défaut",
        "cdu_kbd":      100,
        "vdu_active":   True,
        "vdu_kbd":      100,
        "fccu_active":  True,
        "fccu_kbd":     50,
        "hcu_active":   True,
        "hcu_kbd":      50,
        "coker_active": True,
        "coker_kbd":    40,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    _init_session_state()

    with st.sidebar:
        st.header("🏭 Raffinerie")

        # Radio — lecture/écriture manuelle
        index = 0 if st.session_state["mode_config"] == "Prédéfinie" else 1
        mode = st.radio("Mode", ["Prédéfinie", "Personnalisée"], index=index)
        st.session_state["mode_config"] = mode

        if mode == "Prédéfinie":
            idx = list(CONFIGS.keys()).index(st.session_state["choix_config"])
            choix = st.selectbox("Configuration", options=list(CONFIGS.keys()), index=idx)
            st.session_state["choix_config"] = choix
            config = CONFIGS[choix]

        else:
            st.subheader("CDU")
            cdu = st.slider("CDU (kbd)", 50, 700, st.session_state["cdu_kbd"], 10)
            st.session_state["cdu_kbd"] = cdu

            st.subheader("VDU")
            vdu_active = st.toggle("VDU active", value=st.session_state["vdu_active"])
            st.session_state["vdu_active"] = vdu_active
            if vdu_active:
                vdu = st.slider("VDU (kbd)", 50, 700, st.session_state["vdu_kbd"], 10)
                st.session_state["vdu_kbd"] = vdu

            st.subheader("FCCU")
            fccu_active = st.toggle("FCCU active", value=st.session_state["fccu_active"])
            st.session_state["fccu_active"] = fccu_active
            if fccu_active:
                fccu = st.slider("FCCU (kbd)", 10, 300, st.session_state["fccu_kbd"], 10)
                st.session_state["fccu_kbd"] = fccu

            st.subheader("HCU")
            hcu_active = st.toggle("HCU active", value=st.session_state["hcu_active"])
            st.session_state["hcu_active"] = hcu_active
            if hcu_active:
                hcu = st.slider("HCU (kbd)", 10, 300, st.session_state["hcu_kbd"], 10)
                st.session_state["hcu_kbd"] = hcu

            st.subheader("Coker")
            coker_active = st.toggle("Coker active", value=st.session_state["coker_active"])
            st.session_state["coker_active"] = coker_active
            if coker_active:
                coker = st.slider("Coker (kbd)", 10, 200, st.session_state["coker_kbd"], 10)
                st.session_state["coker_kbd"] = coker

            config = RefineryConfig(
                name="Personnalisée",
                cdu_capacity_kbd   = st.session_state["cdu_kbd"],
                vdu_active         = st.session_state["vdu_active"],
                vdu_capacity_kbd   = st.session_state.get("vdu_kbd", 100),
                fccu_active        = st.session_state["fccu_active"],
                fccu_capacity_kbd  = st.session_state.get("fccu_kbd", 50),
                hcu_active         = st.session_state["hcu_active"],
                hcu_capacity_kbd   = st.session_state.get("hcu_kbd", 50),
                coker_active       = st.session_state["coker_active"],
                coker_capacity_kbd = st.session_state.get("coker_kbd", 40),
            )

    return config


def render_mix_sidebar():
    """
    Affiche le sélecteur de brut/mix dans la sidebar.
    Retourne un dict {nom_brut: fraction} — somme = 1.0
    Synchronisé entre toutes les pages via session_state.
    """
    from data.crudes import CRUDES

    # Initialisation des valeurs par défaut
    defaults = {
        "mode_mix":           "Brut unique",
        "brut_unique":        "Brent",
        "mix_brent":          25,
        "mix_urals":          25,
        "mix_arab_light":     25,
        "mix_sahara_blend":   25,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.sidebar:
        st.divider()
        st.header("🛢️ Brut / Mix")

        index_mode = 0 if st.session_state["mode_mix"] == "Brut unique" else 1
        mode_mix = st.radio("Mode", ["Brut unique", "Mix personnalisé"], index=index_mode)
        st.session_state["mode_mix"] = mode_mix

        if mode_mix == "Brut unique":
            noms = list(CRUDES.keys())
            idx  = noms.index(st.session_state["brut_unique"]) if st.session_state["brut_unique"] in noms else 0
            brut = st.selectbox("Brut", options=noms, index=idx)
            st.session_state["brut_unique"] = brut
            mix = {nom: (1.0 if nom == brut else 0.0) for nom in noms}

        else:
            st.caption("Les % doivent sommer à 100")

            brent = st.slider("Brent (%)",        0, 100, st.session_state["mix_brent"],       5)
            urals = st.slider("Urals (%)",        0, 100, st.session_state["mix_urals"],       5)
            arab  = st.slider("Arab Light (%)",   0, 100, st.session_state["mix_arab_light"],  5)
            sahara= st.slider("Sahara Blend (%)", 0, 100, st.session_state["mix_sahara_blend"],5)

            st.session_state["mix_brent"]        = brent
            st.session_state["mix_urals"]        = urals
            st.session_state["mix_arab_light"]   = arab
            st.session_state["mix_sahara_blend"] = sahara

            total = brent + urals + arab + sahara

            if total == 0:
                st.error("Le total ne peut pas être 0%")
                mix = {"Brent": 0.25, "Urals": 0.25, "Arab Light": 0.25, "Sahara Blend": 0.25}
            elif total != 100:
                st.warning(f"Total : {total}% — doit être 100%")
                mix = {
                    "Brent":        brent  / total,
                    "Urals":        urals  / total,
                    "Arab Light":   arab   / total,
                    "Sahara Blend": sahara / total,
                }
            else:
                st.success("✅ Total : 100%")
                mix = {
                    "Brent":        brent  / 100,
                    "Urals":        urals  / 100,
                    "Arab Light":   arab   / 100,
                    "Sahara Blend": sahara / 100,
                }

    return mix