# refinery/monte_carlo.py
# Simule 1000 scénarios de prix et calcule la distribution des marges

import numpy as np
from refinery.optimizer import calcul_mbr, PRODUCT_PRICES
from data.crudes import CRUDES


def simuler_monte_carlo(mix: dict, n_simulations: int = 1000) -> dict:
    """
    Simule n_simulations scénarios de prix et calcule la MBR pour chacun.

    Pour chaque scénario, on fait varier :
    - le prix de chaque brut (volatilité de 15%)
    - le prix de chaque produit (volatilité de 10%)
    """
    mbrs = []

    for _ in range(n_simulations):

        # --- Faire varier les prix des bruts ---
        # np.random.normal(1, 0.15) génère un chiffre autour de 1
        # avec une variation de ±15% — comme le marché réel
        crudes_perturbes = {}
        for nom, crude in CRUDES.items():
            facteur = np.random.normal(1, 0.15)
            crude.price_usd_bbl = crude.price_usd_bbl * facteur
            crudes_perturbes[nom] = crude

        # --- Faire varier les prix des produits ---
        produits_perturbes = {}
        for produit, prix in PRODUCT_PRICES.items():
            facteur = np.random.normal(1, 0.10)
            produits_perturbes[produit] = prix * facteur

        # --- Calculer la MBR pour ce scénario ---
        mbr = calcul_mbr(mix, capacite_kbd=100)
        mbrs.append(mbr)

    mbrs = np.array(mbrs)

    return {
        "mbrs":          mbrs.tolist(),
        "moyenne":       round(float(np.mean(mbrs)), 2),
        "var_95":        round(float(np.percentile(mbrs, 5)), 2),
        "prob_negative": round(float(np.mean(mbrs < 0) * 100), 1),
    }
