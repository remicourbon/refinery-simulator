# refinery/monte_carlo.py
# Simule 1000 scénarios de prix et calcule la distribution des marges

import numpy as np
from refinery.optimizer import calcul_mbr, PRODUCT_PRICES
from data.crudes import CRUDES


def simuler_monte_carlo(mix: dict,
                        config=None,
                        n_simulations: int = 1000) -> dict:
    """
    Simule n_simulations scénarios de prix.

    Pour chaque scénario :
    - les prix des bruts varient de ±15%
    - les prix des produits varient de ±10%
    - on ne modifie jamais les objets originaux
    """
    mbrs = []

    for _ in range(n_simulations):

        # Prix des bruts perturbés — copies, pas les originaux
        prix_bruts_perturbes = {
            nom: CRUDES[nom].price_usd_bbl * np.random.normal(1, 0.15)
            for nom in CRUDES
        }

        # Prix des produits perturbés — copies, pas les originaux
        prix_produits_perturbes = {
            produit: prix * np.random.normal(1, 0.10)
            for produit, prix in PRODUCT_PRICES.items()
        }

        # Calcul de la MBR avec les prix perturbés
        mbr = calcul_mbr(
            mix,
            config=config,
            prix_bruts=prix_bruts_perturbes,
            prix_produits=prix_produits_perturbes,
        )
        mbrs.append(mbr)

    mbrs = np.array(mbrs)

    return {
        "mbrs":          mbrs.tolist(),
        "moyenne":       round(float(np.mean(mbrs)), 2),
        "var_95":        round(float(np.percentile(mbrs, 5)), 2),
        "prob_negative": round(float(np.mean(mbrs < 0) * 100), 1),
    }

