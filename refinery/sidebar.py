# refinery/sidebar.py
import streamlit as st
from refinery.config import CONFIGS, RefineryConfig


def _init_session_state():
    defaults = {
        "mode_config":          "Prédéfinie",
        "choix_config":         "Défaut",
        "yield_mode":           "md",
        "cdu_kbd":              100,
        "vdu_active":           True,
        "vdu_kbd":              100,
        "fccu_active":          True,
        "fccu_kbd":             50,
        "fccu_sulfur_max":      2.0,
        "hcu_active":           True,
        "hcu_kbd":              50,
        "hcu_sulfur_max":       1.0,
        "coker_active":         True,
        "coker_kbd":            40,
        "reformer_active":      False,
        "reformer_kbd":         0,
        "fo_cut_ratio":         20,   # stocké en % entier (0–50)
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> RefineryConfig:
    _init_session_state()

    with st.sidebar:
        st.header("🏭 Raffinerie")

        # --- Mode prédéfini / personnalisé ---
        index = 0 if st.session_state["mode_config"] == "Prédéfinie" else 1
        mode = st.radio("Mode", ["Prédéfinie", "Personnalisée"], index=index)
        st.session_state["mode_config"] = mode

        if mode == "Prédéfinie":
            idx   = list(CONFIGS.keys()).index(st.session_state["choix_config"])
            choix = st.selectbox("Configuration", options=list(CONFIGS.keys()), index=idx)
            st.session_state["choix_config"] = choix
            config = CONFIGS[choix]

        else:
            # ---- Yield mode ----
            st.subheader("⚙️ Mode de marche")
            yield_mode = st.radio(
                "Profil de yields",
                ["md", "gm"],
                index=0 if st.session_state["yield_mode"] == "md" else 1,
                help="md = mode dégradé (conservative) · gm = grande marge (optimiste)",
            )
            st.session_state["yield_mode"] = yield_mode

            # ---- CDU ----
            st.subheader("CDU")
            cdu = st.slider("CDU (kbd)", 50, 700, st.session_state["cdu_kbd"], 10)
            st.session_state["cdu_kbd"] = cdu

            # ---- VDU ----
            st.subheader("VDU")
            vdu_active = st.toggle("VDU active", value=st.session_state["vdu_active"])
            st.session_state["vdu_active"] = vdu_active
            vdu_kbd = st.session_state["vdu_kbd"]
            if vdu_active:
                vdu_kbd = st.slider("VDU (kbd)", 50, 700, st.session_state["vdu_kbd"], 10)
                st.session_state["vdu_kbd"] = vdu_kbd

            # ---- FCCU ----
            st.subheader("FCCU")
            fccu_active = st.toggle("FCCU active", value=st.session_state["fccu_active"])
            st.session_state["fccu_active"] = fccu_active
            fccu_kbd, fccu_sulfur_max = st.session_state["fccu_kbd"], st.session_state["fccu_sulfur_max"]
            if fccu_active:
                fccu_kbd = st.slider("FCCU (kbd)", 10, 300, st.session_state["fccu_kbd"], 10)
                fccu_sulfur_max = st.slider(
                    "Soufre max FCCU (%)", 0.5, 5.0, float(st.session_state["fccu_sulfur_max"]), 0.1,
                    help="Throughput réduit si le soufre du brut dépasse ce seuil",
                )
                st.session_state["fccu_kbd"]        = fccu_kbd
                st.session_state["fccu_sulfur_max"] = fccu_sulfur_max

            # ---- HCU ----
            st.subheader("HCU")
            hcu_active = st.toggle("HCU active", value=st.session_state["hcu_active"])
            st.session_state["hcu_active"] = hcu_active
            hcu_kbd, hcu_sulfur_max = st.session_state["hcu_kbd"], st.session_state["hcu_sulfur_max"]
            if hcu_active:
                hcu_kbd = st.slider("HCU (kbd)", 10, 300, st.session_state["hcu_kbd"], 10)
                hcu_sulfur_max = st.slider(
                    "Soufre max HCU (%)", 0.1, 3.0, float(st.session_state["hcu_sulfur_max"]), 0.1,
                    help="Le HCU est plus sensible au soufre que la FCCU",
                )
                st.session_state["hcu_kbd"]        = hcu_kbd
                st.session_state["hcu_sulfur_max"] = hcu_sulfur_max

            # ---- Coker ----
            st.subheader("Coker")
            coker_active = st.toggle("Coker active", value=st.session_state["coker_active"])
            st.session_state["coker_active"] = coker_active
            coker_kbd = st.session_state["coker_kbd"]
            if coker_active:
                coker_kbd = st.slider("Coker (kbd)", 10, 200, st.session_state["coker_kbd"], 10)
                st.session_state["coker_kbd"] = coker_kbd

            # ---- Reformer ----
            st.subheader("Reformer")
            reformer_active = st.toggle("Reformer actif", value=st.session_state["reformer_active"])
            st.session_state["reformer_active"] = reformer_active
            reformer_kbd = st.session_state["reformer_kbd"]
            if reformer_active:
                reformer_kbd = st.slider("Reformer (kbd)", 5, 150, max(st.session_state["reformer_kbd"], 5), 5)
                st.session_state["reformer_kbd"] = reformer_kbd

            # ---- FO Blender ----
            st.subheader("FO Blender")
            fo_cut_pct = st.slider(
                "Taux de cutter (%)", 5, 50, st.session_state["fo_cut_ratio"], 5,
                help="Fraction massique de cutter (LCO / gasoil) dans le fuel oil final",
            )
            st.session_state["fo_cut_ratio"] = fo_cut_pct

            config = RefineryConfig(
                name                  = "Personnalisée",
                yield_mode            = st.session_state["yield_mode"],
                cdu_capacity_kbd      = st.session_state["cdu_kbd"],
                vdu_active            = st.session_state["vdu_active"],
                vdu_capacity_kbd      = vdu_kbd,
                fccu_active           = st.session_state["fccu_active"],
                fccu_capacity_kbd     = fccu_kbd,
                fccu_sulfur_max       = fccu_sulfur_max,
                hcu_active            = st.session_state["hcu_active"],
                hcu_capacity_kbd      = hcu_kbd,
                hcu_sulfur_max        = hcu_sulfur_max,
                coker_active          = st.session_state["coker_active"],
                coker_capacity_kbd    = coker_kbd,
                reformer_active       = st.session_state["reformer_active"],
                reformer_capacity_kbd = reformer_kbd,
                fo_cut_ratio          = fo_cut_pct / 100.0,
            )

    return config


def render_mix_sidebar() -> dict:
    """
    Sélecteur de brut / mix dans la sidebar.
    Retourne un dict {nom_brut: fraction} — somme = 1.0
    """
    from data.crudes import CRUDES

    defaults = {
        "mode_mix":         "Brut unique",
        "brut_unique":      "Brent",
        "mix_brent":        25,
        "mix_urals":        25,
        "mix_arab_light":   25,
        "mix_sahara_blend": 25,
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
            brent  = st.slider("Brent (%)",        0, 100, st.session_state["mix_brent"],       5)
            urals  = st.slider("Urals (%)",         0, 100, st.session_state["mix_urals"],       5)
            arab   = st.slider("Arab Light (%)",    0, 100, st.session_state["mix_arab_light"],  5)
            sahara = st.slider("Sahara Blend (%)",  0, 100, st.session_state["mix_sahara_blend"],5)

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
                st.success("Total : 100%")
                mix = {
                    "Brent":        brent  / 100,
                    "Urals":        urals  / 100,
                    "Arab Light":   arab   / 100,
                    "Sahara Blend": sahara / 100,
                }

    return mix