# refinery/optimizer.py
from scipy.optimize import minimize
from data.crudes import CRUDES
from refinery.config import CONFIGS
from refinery.balance import run_balance

PRODUCT_PRICES = {
    "LPG":      55.0,
    "Naphtha":  75.0,
    "Kerosene": 95.0,
    "Gasoil":   90.0,
    "Diesel":   95.0,
    "Gasoline": 92.0,
    "HSFO":     45.0,
    "Pet_coke": 30.0,
}


def calcul_soufre_mix(mix: dict) -> float:
    return sum(
        CRUDES[nom].sulfur_pct * fraction
        for nom, fraction in mix.items()
        if fraction > 0
    )


def calcul_mbr(mix: dict,
               config=None,
               prix_bruts: dict = None,
               prix_produits: dict = None) -> float:
    if config is None:
        config = CONFIGS["Défaut"]

    _prix_bruts    = prix_bruts    if prix_bruts    is not None else {n: CRUDES[n].price_usd_bbl for n in CRUDES}
    _prix_produits = prix_produits if prix_produits is not None else PRODUCT_PRICES

    cout_brut = sum(
        _prix_bruts[nom] * fraction
        for nom, fraction in mix.items()
        if fraction > 0
    )

    valeur_produits = 0.0
    cap_totale = config.cdu_capacity_kbd

    for nom, fraction in mix.items():
        if fraction <= 0:
            continue

        crude = CRUDES[nom]

        from refinery.config import RefineryConfig
        config_fraction = RefineryConfig(
            name=config.name,
            cdu_capacity_kbd   = cap_totale            * fraction,
            vdu_active         = config.vdu_active,
            vdu_capacity_kbd   = config.vdu_capacity_kbd   * fraction,
            fccu_active        = config.fccu_active,
            fccu_capacity_kbd  = config.fccu_capacity_kbd  * fraction,
            hcu_active         = config.hcu_active,
            hcu_capacity_kbd   = config.hcu_capacity_kbd   * fraction,
            coker_active       = config.coker_active,
            coker_capacity_kbd = config.coker_capacity_kbd * fraction,
        )

        df = run_balance(crude, config=config_fraction)

        for produit, row in df.iterrows():
            prix = _prix_produits.get(produit, 0)
            valeur_produits += row["kbd"] * prix * 1000 / (cap_totale * 1000)

    return valeur_produits - cout_brut


def optimiser_mix(config=None,
                  soufre_max: float = 2.0,
                  mix_min: float = 0.10,
                  mix_max: float = 0.60) -> dict:
    if config is None:
        config = CONFIGS["Défaut"]

    # Protection contre les valeurs extrêmes
    mix_min = max(mix_min, 0.01)
    mix_max = min(mix_max, 1.0)

    noms = list(CRUDES.keys())
    n    = len(noms)

    def objectif(fractions):
        mix = {noms[i]: fractions[i] for i in range(n)}
        return -calcul_mbr(mix, config=config)

    contraintes = [
        {"type": "eq", "fun": lambda x: sum(x) - 1},
        {"type": "ineq", "fun": lambda x: soufre_max - sum(
            CRUDES[noms[i]].sulfur_pct * x[i] for i in range(n)
        )},
    ]

    bornes = [(mix_min, mix_max)] * n
    x0     = [1 / n] * n

    resultat = minimize(objectif, x0, method="SLSQP",
                        bounds=bornes, constraints=contraintes)

    mix_optimal  = {noms[i]: round(resultat.x[i], 3) for i in range(n)}
    mbr_optimale = round(-resultat.fun, 2)

    return {
        "mix":    mix_optimal,
        "mbr":    mbr_optimale,
        "soufre": round(calcul_soufre_mix(mix_optimal), 2),
    }