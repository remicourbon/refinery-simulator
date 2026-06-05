"""
refinery/balance.py
-------------------
Pattern pool : chaque unité dépose ses sorties, la suivante pioche sa charge.
Rien ne se perd — ce qui n'est pas valorisé devient HSFO.

Règles :
  - CDU : toujours active, capacité paramétrable
  - VDU : optionnelle, limitée par sa capacité
  - FCCU + HCU : optionnels, reçoivent le VGO proportionnellement à leurs capacités
  - Coker : optionnel, traite le résidu vide
  - Tout flux sans preneur → HSFO
"""

import pandas as pd
from refinery.units import run_cdu, run_vdu, run_fccu, run_hcu, run_coker, BBL_PER_TON

M3_TO_BBL = 6.2898

def _kbd_to_t_h(kbd, density):
    """Convertit une capacité en kbd en t/h."""
    return kbd * 1000 / 24 / M3_TO_BBL * density


def run_balance(crude, config) -> pd.DataFrame:
    """
    Calcule le bilan matière complet.
    Tous les flux sont tracés — rien ne disparaît.
    """

    # Pool des produits finis — commence à zéro
    pool = {
        "LPG":      0.0,
        "Naphtha":  0.0,
        "Kerosene": 0.0,
        "Gasoil":   0.0,
        "Diesel":   0.0,
        "Gasoline": 0.0,
        "HSFO":     0.0,
        "Pet_coke": 0.0,
    }

    # ÉTAPE 1 — CDU (toujours active)
    cdu_t_h = _kbd_to_t_h(config.cdu_capacity_kbd, crude.density)
    cdu = run_cdu(cdu_t_h, crude)
    pool["LPG"]      += cdu["LPG"]
    pool["Naphtha"]  += cdu["Naphtha"]
    pool["Kerosene"] += cdu["Kerosene"]
    pool["Gasoil"]   += cdu["Gasoil"]
    atm_resid = cdu["Atm_resid"]

    # ÉTAPE 2 — VDU
    if config.vdu_active:
        vdu_max_t_h = _kbd_to_t_h(config.vdu_capacity_kbd, crude.density)
        vdu_charge  = min(atm_resid, vdu_max_t_h)
        vdu_surplus = atm_resid - vdu_charge
        vdu = run_vdu(vdu_charge, crude)
        vgo       = vdu["VGO"]
        vac_resid = vdu["Vac_resid"]
        pool["HSFO"] += vdu_surplus
    else:
        vgo       = 0.0
        vac_resid = 0.0
        pool["HSFO"] += atm_resid

    # ÉTAPE 3 — Répartition du VGO entre FCCU et HCU
    cap_fccu = config.fccu_capacity_kbd if config.fccu_active else 0.0
    cap_hcu  = config.hcu_capacity_kbd  if config.hcu_active  else 0.0
    cap_conv = cap_fccu + cap_hcu

    if cap_conv > 0 and vgo > 0:
        vgo_fccu = vgo * (cap_fccu / cap_conv)
        vgo_hcu  = vgo * (cap_hcu  / cap_conv)
    else:
        vgo_fccu = 0.0
        vgo_hcu  = 0.0

    pool["HSFO"] += vgo - vgo_fccu - vgo_hcu

    # ÉTAPE 4 — FCCU
    if config.fccu_active and vgo_fccu > 0:
        fccu = run_fccu(vgo_fccu)
        pool["LPG"]      += fccu["LPG"]
        pool["Gasoline"] += fccu["Gasoline"]
        pool["Gasoil"]   += fccu["LCO"]
        pool["HSFO"]     += fccu["Slurry"]

    # ÉTAPE 5 — HCU
    if config.hcu_active and vgo_hcu > 0:
        hcu = run_hcu(vgo_hcu)
        pool["LPG"]      += hcu["LPG"]
        pool["Naphtha"]  += hcu["Naphtha"]
        pool["Kerosene"] += hcu["Kerosene"]
        pool["Diesel"]   += hcu["Diesel"]
        pool["HSFO"]     += hcu["Resid"]

    # ÉTAPE 6 — Coker
    if config.coker_active and vac_resid > 0:
        coker_max_t_h = _kbd_to_t_h(config.coker_capacity_kbd, crude.density)
        coker_charge  = min(vac_resid, coker_max_t_h)
        coker_surplus = vac_resid - coker_charge
        coker = run_coker(coker_charge)
        pool["LPG"]      += coker["LPG"]
        pool["Naphtha"]  += coker["Naphtha"]
        pool["Gasoil"]   += coker["Gasoil"]
        pool["Pet_coke"] += coker["Pet_coke"]
        pool["HSFO"]     += coker_surplus
    else:
        pool["HSFO"] += vac_resid

    # ÉTAPE 7 — Mise en forme
    total_t_h = sum(pool.values())
    rows = []
    for produit, t_h in pool.items():
        pct_mt = 100 * t_h / total_t_h if total_t_h > 0 else 0
        kbd    = t_h * BBL_PER_TON.get(produit, 7.45) * 24 / 1000
        rows.append({
            "Produit": produit,
            "t/h":     round(t_h, 1),
            "%mt":     round(pct_mt, 1),
            "kbd":     round(kbd, 2),
        })

    return pd.DataFrame(rows).set_index("Produit")
