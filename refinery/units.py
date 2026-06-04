# refinery/units.py
# Chaque fonction = une unité de la raffinerie
# Entrée : une charge en t/h — Sortie : un dictionnaire de produits en t/h

# Constante de conversion : barils par tonne, selon le produit
# Plus un produit est léger, plus il y a de barils par tonne
BBL_PER_TON = {
    "LPG":      11.00,
    "Naphtha":   8.90,
    "Kerosene":  7.88,
    "Gasoil":    7.45,
    "Diesel":    7.45,
    "Gasoline":  8.33,
    "HSFO":      6.34,
    "Pet_coke":  5.50,
}


def run_cdu(throughput_t_h: float, crude) -> dict:
    # La CDU distille le brut brut en coupes atmosphériques
    # Les yields viennent du brut — chaque pétrole a sa propre signature
    return {
        "LPG":       throughput_t_h * crude.lpg_yield,
        "Naphtha":   throughput_t_h * crude.naphtha_yield,
        "Kerosene":  throughput_t_h * crude.kerosene_yield,
        "Gasoil":    throughput_t_h * crude.gasoil_yield,
        "Atm_resid": throughput_t_h * crude.atm_resid_yield,
    }


def run_vdu(atm_resid_t_h: float, crude) -> dict:
    # La VDU fractionne le résidu atmosphérique sous vide
    # Elle produit du VGO (charge des unités de conversion) et un résidu vide
    return {
        "VGO":       atm_resid_t_h * crude.vgo_yield,
        "Vac_resid": atm_resid_t_h * crude.vac_resid_yield,
    }


def run_fccu(vgo_t_h: float) -> dict:
    # La FCCU craque le VGO en produits légers à haute valeur
    # L'essence FCC est le produit phare
    return {
        "LPG":      vgo_t_h * 0.12,
        "Gasoline": vgo_t_h * 0.48,
        "LCO":      vgo_t_h * 0.20,  # gazole de craquage
        "Slurry":   vgo_t_h * 0.08,  # fond de colonne → fuel oil
    }


def run_hcu(vgo_t_h: float) -> dict:
    # Le HCU hydrocraque le VGO en distillats premium (jet, diesel)
    # Produit de meilleure qualité que la FCCU mais consomme de l'hydrogène
    return {
        "LPG":      vgo_t_h * 0.05,
        "Naphtha":  vgo_t_h * 0.20,
        "Kerosene": vgo_t_h * 0.30,
        "Diesel":   vgo_t_h * 0.38,
        "Resid":    vgo_t_h * 0.07,
    }


def run_coker(vac_resid_t_h: float) -> dict:
    # Le Coker valorise le résidu vide — le "fond de barril"
    # Ce que les autres unités ne veulent pas, le Coker le traite
    return {
        "LPG":      vac_resid_t_h * 0.06,
        "Naphtha":  vac_resid_t_h * 0.12,
        "Gasoil":   vac_resid_t_h * 0.38,
        "Pet_coke": vac_resid_t_h * 0.30,
    }