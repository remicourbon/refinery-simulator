# refinery/optimizer.py
# Trouve le mix de bruts qui maximise la marge de raffinage
# On utilise scipy — une bibliothèque d'optimisation mathématique

from scipy.optimize import minimize
from data.crudes import CRUDES
from refinery.balance import run_balance

# Prix des produits finis ($/bbl) — crack spreads par rapport au Brent
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


def calcul_mbr(mix: dict, capacite_kbd: float = 100.0) -> float:
    """
    Calcule la marge brute de raffinage pour un mix de bruts donné.
    mix = {"Brent": 0.3, "Urals": 0.5, ...} — les fractions doivent sommer à 1
    """
    # Coût d'achat du brut (moyenne pondérée)
    cout_brut = sum(
        CRUDES[nom].price_usd_bbl * fraction
        for nom, fraction in mix.items()
    )

    # Valeur des produits — on calcule le bilan pour chaque brut
    # puis on pondère par sa fraction dans le mix
    valeur_produits = 0.0
    for nom, fraction in mix.items():
        crude = CRUDES[nom]
        df = run_balance(crude, cdu_capacity_kbd=capacite_kbd * fraction)
        for produit, row in df.iterrows():
            prix = PRODUCT_PRICES.get(produit, 0)
            valeur_produits += row["kbd"] * prix * 1000 / (capacite_kbd * 1000)

    mbr = valeur_produits - cout_brut
    return mbr


def optimiser_mix(capacite_kbd: float = 100.0) -> dict:
    """
    Trouve le mix optimal qui maximise la MBR.
    Retourne un dictionnaire avec les fractions optimales et la MBR.
    """
    noms = list(CRUDES.keys())
    n = len(noms)

    def objectif(fractions):
        # scipy minimise — on retourne le négatif pour maximiser
        mix = {noms[i]: fractions[i] for i in range(n)}
        return -calcul_mbr(mix, capacite_kbd)

    # Contraintes : les fractions doivent sommer à 1
    contraintes = {"type": "eq", "fun": lambda x: sum(x) - 1}

    # Bornes : chaque brut entre 10% et 60% du mix
    # Une raffinerie ne peut pas traiter 100% d'un seul brut
    bornes = [(0.10, 0.60)] * n

    # Point de départ : mix égal entre tous les bruts
    x0 = [1 / n] * n

    resultat = minimize(objectif, x0, method="SLSQP",
                        bounds=bornes, constraints=contraintes)

    mix_optimal = {noms[i]: round(resultat.x[i], 3) for i in range(n)}
    mbr_optimale = round(-resultat.fun, 2)

    return {
        "mix": mix_optimal,
        "mbr": mbr_optimale,
    }