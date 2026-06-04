# refinery/balance.py
# Orchestre le passage du brut à travers toutes les unités
# C'est ici qu'on assemble les flux — le "chef d'orchestre"

import pandas as pd
from refinery.units import run_cdu, run_vdu, run_fccu, run_hcu, run_coker, BBL_PER_TON


def run_balance(crude, cdu_capacity_kbd: float = 100.0) -> pd.DataFrame:
    # cdu_capacity_kbd = capacité de la CDU en milliers de barils/jour

    # --- Étape 0 : convertir kbd → t/h ---
    # kbd → bbl/h → m³/h → t/h
    cdu_bbl_h  = cdu_capacity_kbd * 1000 / 24   # milliers de barils/jour → barils/heure
    cdu_m3_h   = cdu_bbl_h / 6.2898             # barils/heure → m³/heure
    cdu_t_h    = cdu_m3_h * crude.density        # m³/heure → tonnes/heure

    # --- Étape 1 : CDU ---
    cdu = run_cdu(cdu_t_h, crude)

    # --- Étape 2 : VDU — reçoit le résidu de la CDU ---
    vdu = run_vdu(cdu["Atm_resid"], crude)

    # --- Étape 3 : on répartit le VGO 50/50 entre FCCU et HCU ---
    vgo_fccu = vdu["VGO"] * 0.5
    vgo_hcu  = vdu["VGO"] * 0.5

    # --- Étape 4 : FCCU et HCU en parallèle ---
    fccu = run_fccu(vgo_fccu)
    hcu  = run_hcu(vgo_hcu)

    # --- Étape 5 : Coker — reçoit le résidu vide ---
    coker = run_coker(vdu["Vac_resid"])

    # --- Étape 6 : on additionne par produit final ---
    products = {
        "LPG":      cdu["LPG"]      + fccu["LPG"]     + hcu["LPG"]     + coker["LPG"],
        "Naphtha":  cdu["Naphtha"]  + hcu["Naphtha"]  + coker["Naphtha"],
        "Kerosene": cdu["Kerosene"] + hcu["Kerosene"],
        "Gasoil":   cdu["Gasoil"]   + fccu["LCO"]     + coker["Gasoil"],
        "Diesel":   hcu["Diesel"],
        "Gasoline": fccu["Gasoline"],
        "HSFO":     fccu["Slurry"],
        "Pet_coke": coker["Pet_coke"],
    }

    # --- Étape 7 : calculer %mt, %vol, kbd ---
    total_t_h = sum(products.values())

    rows = []
    for produit, t_h in products.items():
        pct_mt = 100 * t_h / total_t_h
        kbd    = t_h * BBL_PER_TON.get(produit, 7.45) * 24 / 1000
        rows.append({
            "Produit": produit,
            "t/h":     round(t_h, 1),
            "%mt":     round(pct_mt, 1),
            "kbd":     round(kbd, 2),
        })

    df = pd.DataFrame(rows).set_index("Produit")
    return df