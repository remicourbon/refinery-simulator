# Optimiseur de mix brut — maximise la MBR
# Les objets Crude ne sont jamais modifiés directement

from scipy.optimize import minimize
from data.crudes import CRUDES
from refinery.config import CONFIGS
from refinery.balance import run_balance

# Prix des produits finis ($/bbl) — référence de base
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


def calcul_mbr(mix: dict,
               config=None,
               prix_bruts: dict = None,
               prix_produits: dict = None) -> float:
    """
    Calcule la MBR pour un mix de bruts donné.

    mix          : {"Brent": 0.3, "Urals": 0.5, ...} — fractions summing to 1
    config       : configuration de la raffinerie
    prix_bruts   : dict optionnel {"Brent": 85.0, ...} — pour le Monte Carlo
    prix_produits: dict optionnel {"Gasoline": 92.0, ...} — pour le Monte Carlo
    """
    if config is None:
        config = CONFIGS["Défaut"]

    # On utilise les prix fournis, ou les prix de référence par défaut
    _prix_bruts    = prix_bruts    if prix_bruts    is not None else {n: CRUDES[n].price_usd_bbl for n in CRUDES}
    _prix_produits = prix_produits if prix_produits is not None else PRODUCT_PRICES

    # Coût d'achat du brut — moyenne pondérée
    cout_brut = sum(
        _prix_bruts[nom] * fraction
        for nom, fraction in mix.items()
        if fraction > 0
    )

    # Valeur des produits — bilan pour chaque brut, pondéré par sa fraction
    valeur_produits = 0.0
    cap_totale = config.cdu_capacity_kbd

    for nom, fraction in mix.items():
        if fraction <= 0:
            continue

        crude = CRUDES[nom]

        # Config proportionnelle à la fraction du brut dans le mix
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


def optimiser_mix(config=None) -> dict:
    """
    Trouve le mix optimal qui maximise la MBR.
    """
    if config is None:
        config = CONFIGS["Défaut"]

    noms = list(CRUDES.keys())
    n    = len(noms)

    def objectif(fractions):
        mix = {noms[i]: fractions[i] for i in range(n)}
        return -calcul_mbr(mix, config=config)

    contraintes = {"type": "eq", "fun": lambda x: sum(x) - 1}
    bornes      = [(0.10, 0.60)] * n
    x0          = [1 / n] * n

    resultat = minimize(objectif, x0, method="SLSQP",
                        bounds=bornes, constraints=contraintes)

    mix_optimal  = {noms[i]: round(resultat.x[i], 3) for i in range(n)}
    mbr_optimale = round(-resultat.fun, 2)

    return {"mix": mix_optimal, "mbr": mbr_optimale}

