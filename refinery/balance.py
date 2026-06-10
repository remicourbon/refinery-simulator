"""
refinery/balance.py
-------------------
Moteur de bilan matière.

Séquence d'exécution :
  CDU → VDU → [répartition VGO] → FCCU / HCU → Coker → Reformer → FO_Blender

Règles de conservation :
  - Rien ne se crée ni ne disparaît
  - Tout flux sans preneur devient HSFO
  - isBalanced() vérifié après chaque unité (tolérance configurable)
"""

import pandas as pd
from collections import OrderedDict

from refinery.units import (
    CDU, VDU, FCCU, HCU, COKER, REFORMER, FO_BLENDER,
    RefineryState, BBL_PER_TON, kbd_to_t_h, M3_TO_BBL,
)


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------

def _split_vgo(state: RefineryState, cap_fccu: float, cap_hcu: float) -> None:
    """
    Répartit le VGO entre FCCU et HCU proportionnellement aux capacités.
    Chaque unité piochera ensuite dans son propre slot du pool.
    Le surplus (si les deux sont inactives) reste en HSFO.
    """
    vgo = state.pool.pop("vgo", 0.0)
    cap_total = cap_fccu + cap_hcu

    if cap_total > 0 and vgo > 0:
        state.pool["vgo_fccu"] = vgo * cap_fccu / cap_total
        state.pool["vgo_hcu"]  = vgo * cap_hcu  / cap_total
    else:
        state.output.HSFO += vgo


def _flush_pool_to_hsfo(state: RefineryState) -> None:
    """
    Tout ce qui reste dans le pool en fin de chaîne n'a pas trouvé preneur.
    On le bascule en HSFO pour maintenir la conservation de la masse.
    """
    for key in list(state.pool.keys()):
        state.output.HSFO += state.pool.pop(key)


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def run_balance(crude, config) -> pd.DataFrame:
    """
    Calcule le bilan matière complet pour un brut et une configuration donnés.

    Parameters
    ----------
    crude  : objet Crude (density, yields, sulfur_pct, ...)
    config : objet RefineryConfig

    Returns
    -------
    pd.DataFrame avec index = produits, colonnes = [%mt, %vol, kbd]
    """

    # Charge initiale (t/h)
    total_input = kbd_to_t_h(config.cdu_capacity_kbd, crude.density)
    state = RefineryState(total_input_t_h=total_input)

    # ------------------------------------------------------------------
    # Construction de la séquence d'unités (OrderedDict pour garder l'ordre)
    # ------------------------------------------------------------------
    units: OrderedDict = OrderedDict()

    # CDU — toujours active
    units["CDU"] = CDU(max_rate_kbd=config.cdu_capacity_kbd)

    # VDU
    if config.vdu_active:
        units["VDU"] = VDU(max_rate_kbd=config.vdu_capacity_kbd)

    # FCCU
    if config.fccu_active:
        fccu = FCCU(
            max_rate_kbd=config.fccu_capacity_kbd,
            sulfur_max=getattr(config, "fccu_sulfur_max", 999.0),
        )
        if hasattr(config, "yield_mode"):
            fccu.set_default(config.yield_mode)
        units["FCCU"] = fccu

    # HCU
    if config.hcu_active:
        hcu = HCU(
            max_rate_kbd=config.hcu_capacity_kbd,
            sulfur_max=getattr(config, "hcu_sulfur_max", 999.0),
        )
        if hasattr(config, "yield_mode"):
            hcu.set_default(config.yield_mode)
        units["HCU"] = hcu

    # Coker
    if config.coker_active:
        coker = COKER(max_rate_kbd=config.coker_capacity_kbd)
        if hasattr(config, "yield_mode"):
            coker.set_default(config.yield_mode)
        units["Coker"] = coker

    # Reformer
    if getattr(config, "reformer_active", False):
        reformer = REFORMER(max_rate_kbd=getattr(config, "reformer_capacity_kbd", 0.0))
        if hasattr(config, "yield_mode"):
            reformer.set_default(config.yield_mode)
        units["Reformer"] = reformer

    # FO Blender — toujours actif (gère les fonds de barril)
    units["FO_Blender"] = FO_BLENDER(
        fo_cut_ratio=getattr(config, "fo_cut_ratio", 0.20)
    )

    # ------------------------------------------------------------------
    # Exécution de la chaîne
    # ------------------------------------------------------------------

    # Cas spécial : répartition VGO avant FCCU/HCU
    cap_fccu = config.fccu_capacity_kbd if config.fccu_active else 0.0
    cap_hcu  = config.hcu_capacity_kbd  if config.hcu_active  else 0.0

    for name, unit in units.items():

        # Juste avant FCCU : répartir le VGO entre FCCU et HCU
        if name == "FCCU":
            _split_vgo(state, cap_fccu, cap_hcu)

        # Avant le Reformer : alimenter son pool avec le Naphtha accumulé
        if name == "Reformer":
            naphtha_to_reform = state.output.Naphtha
            state.output.Naphtha = 0.0
            state.pool["reformer_feed"] = naphtha_to_reform

        unit.process_unit(crude=crude, state=state)

        # Vérification conservation de la masse
        if not state.is_balanced(eps=max(total_input * 0.02, 1.0)):
            raise ValueError(
                f"Bilan non équilibré après {name} : "
                f"input={state.input:.2f} t/h, "
                f"total={state.total():.2f} t/h, "
                f"écart={state.residual():.2f} t/h"
            )

    # Coker HGO restant → HSFO si pas de HCU pour le prendre
    state.pool["vac_tar_spill"] = state.pool.pop("coker_hgo", 0.0)

    # Tout ce qui reste dans le pool → HSFO
    _flush_pool_to_hsfo(state)

    # ------------------------------------------------------------------
    # Mise en forme du résultat
    # ------------------------------------------------------------------
    output_dict = state.output.as_dict()
    total_t_h   = state.output.total()

    # Débit entrant en kbd (pour le calcul %vol)
    kbd_entrant = total_input / crude.density * M3_TO_BBL * 24 / 1000

    rows = []
    for produit, t_h in output_dict.items():
        if total_t_h > 0:
            pct_mt = 100 * t_h / total_t_h
        else:
            pct_mt = 0.0

        kbd = t_h * BBL_PER_TON.get(produit, 7.45) * 24 / 1000

        if kbd_entrant > 0:
            pct_vol = 100 * kbd / kbd_entrant
        else:
            pct_vol = 0.0

        rows.append({
            "Produit": produit,
            "%mt":     round(pct_mt, 1),
            "%vol":    round(pct_vol, 1),
            "kbd":     round(kbd, 2),
        })

    return pd.DataFrame(rows).set_index("Produit")
