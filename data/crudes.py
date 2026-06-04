# data/crudes.py
# Les 4 bruts avec leurs propriétés et rendements

class Crude:
    def __init__(self,
                 name: str,
                 api: float,
                 density: float,
                 lpg_yield: float,
                 naphtha_yield: float,
                 kerosene_yield: float,
                 gasoil_yield: float,
                 atm_resid_yield: float,
                 vgo_yield: float,
                 vac_resid_yield: float,
                 sulfur_pct: float,
                 price_usd_bbl: float):

        self.name = name
        self.api = api                          # degré API — plus élevé = plus léger
        self.density = density                  # t/m³

        # Yields CDU — somment à 1.0
        self.lpg_yield = lpg_yield
        self.naphtha_yield = naphtha_yield
        self.kerosene_yield = kerosene_yield
        self.gasoil_yield = gasoil_yield
        self.atm_resid_yield = atm_resid_yield

        # Yields VDU — somment à 1.0
        self.vgo_yield = vgo_yield
        self.vac_resid_yield = vac_resid_yield

        self.sulfur_pct = sulfur_pct            # % soufre
        self.price_usd_bbl = price_usd_bbl      # prix $/bbl


CRUDES = {
    "Brent": Crude(
        name="Brent", api=38.3, density=0.835,
        lpg_yield=0.02, naphtha_yield=0.18, kerosene_yield=0.12,
        gasoil_yield=0.28, atm_resid_yield=0.40,
        vgo_yield=0.70, vac_resid_yield=0.30,
        sulfur_pct=0.35, price_usd_bbl=85.0,
    ),
    "Urals": Crude(
        name="Urals", api=31.1, density=0.871,
        lpg_yield=0.01, naphtha_yield=0.14, kerosene_yield=0.10,
        gasoil_yield=0.25, atm_resid_yield=0.50,
        vgo_yield=0.60, vac_resid_yield=0.40,
        sulfur_pct=1.35, price_usd_bbl=70.0,
    ),
    "Arab Light": Crude(
        name="Arab Light", api=32.8, density=0.860,
        lpg_yield=0.02, naphtha_yield=0.15, kerosene_yield=0.11,
        gasoil_yield=0.24, atm_resid_yield=0.48,
        vgo_yield=0.58, vac_resid_yield=0.42,
        sulfur_pct=1.80, price_usd_bbl=81.0,
    ),
    "Sahara Blend": Crude(
        name="Sahara Blend", api=43.5, density=0.808,
        lpg_yield=0.03, naphtha_yield=0.22, kerosene_yield=0.15,
        gasoil_yield=0.32, atm_resid_yield=0.28,
        vgo_yield=0.75, vac_resid_yield=0.25,
        sulfur_pct=0.10, price_usd_bbl=88.0,
    ),
}
