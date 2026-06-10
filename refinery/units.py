"""
refinery/units.py
-----------------
Chaque unité est une classe héritant de RefineryUnits.
Yields paramétrables, contrainte soufre sur FCCU et HCU,
Reformer et FO_Blender inclus.

Règle fondamentale : la somme des yields de chaque unité = 1.0
Tout flux est soit un produit fini, soit réinjecté dans le pool.
Rien ne disparaît.
"""

from abc import ABC, abstractmethod
from collections import defaultdict

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

M3_TO_BBL = 6.2898

BBL_PER_TON = {
    "LPG":      11.00,
    "Naphtha":   8.90,
    "Kerosene":  7.88,
    "Gasoil":    7.45,
    "Diesel":    7.45,
    "Gasoline":  8.33,
    "HSFO":      6.34,
    "Pet_coke":  5.50,
    "H2":        8.00,
}

# Yields prédéfinis — TOUS doivent sommer à 1.0
# "md" = mode dégradé, "gm" = grande marge
FCCU_DEFAULTS = {
    #                LPG    Gasoline  LCO    Slurry  Coke_gas  Other   SUM
    "md": {"LPG": 0.05, "Gasoline": 0.35, "LCO": 0.20, "Slurry": 0.09, "Coke_gas": 0.13, "Other": 0.18},  # 1.00
    "gm": {"LPG": 0.05, "Gasoline": 0.75, "LCO": 0.05, "Slurry": 0.09, "Coke_gas": 0.03, "Other": 0.03},  # 1.00
}

HCU_DEFAULTS = {
    #               LPG   Naphtha  Kerosene  Diesel  Gasoil  Resid  H2_cons  SUM
    "md": {"LPG": 0.03, "Naphtha": 0.10, "Kerosene": 0.17, "Diesel": 0.21, "Gasoil": 0.12, "Resid": 0.27, "H2_cons": 0.10},  # 1.00
    "gm": {"LPG": 0.03, "Naphtha": 0.14, "Kerosene": 0.35, "Diesel": 0.00, "Gasoil": 0.28, "Resid": 0.10, "H2_cons": 0.10},  # 1.00
}

COKER_DEFAULTS = {
    #                LPG    Naphtha  Kerosene  Gasoil   HGO    Pet_coke  SUM
    "md": {"LPG": 0.111, "Naphtha": 0.125, "Kerosene": 0.098, "Gasoil": 0.076, "HGO": 0.307, "Pet_coke": 0.283},  # 1.00
    "gm": {"LPG": 0.061, "Naphtha": 0.125, "Kerosene": 0.098, "Gasoil": 0.126, "HGO": 0.307, "Pet_coke": 0.283},  # 1.00
}

REFORMER_DEFAULTS = {
    #               LPG   Naphtha_light  Gasoline   H2    C1C2   Gas   SUM
    "md": {"LPG": 0.09, "Naphtha_light": 0.10, "Gasoline": 0.76, "H2": 0.02, "C1C2": 0.02, "Gas": 0.01},  # 1.00
    "gm": {"LPG": 0.05, "Naphtha_light": 0.12, "Gasoline": 0.76, "H2": 0.02, "C1C2": 0.03, "Gas": 0.02},  # 1.00
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def kbd_to_t_h(kbd: float, density: float) -> float:
    """Capacité en kbd → débit en t/h."""
    return kbd * 1000 / 24 / M3_TO_BBL * density


# ---------------------------------------------------------------------------
# Objets de transfert
# ---------------------------------------------------------------------------

class RefineryOutput:
    """Accumule les produits finis (t/h) au fil du traitement."""

    def __init__(self):
        self.LPG:      float = 0.0
        self.Naphtha:  float = 0.0
        self.Kerosene: float = 0.0
        self.Gasoil:   float = 0.0
        self.Diesel:   float = 0.0
        self.Gasoline: float = 0.0
        self.HSFO:     float = 0.0
        self.Pet_coke: float = 0.0
        self.H2:       float = 0.0

    def total(self) -> float:
        return (self.LPG + self.Naphtha + self.Kerosene + self.Gasoil
                + self.Diesel + self.Gasoline + self.HSFO + self.Pet_coke + self.H2)

    def as_dict(self) -> dict:
        return {
            "LPG":      self.LPG,
            "Naphtha":  self.Naphtha,
            "Kerosene": self.Kerosene,
            "Gasoil":   self.Gasoil,
            "Diesel":   self.Diesel,
            "Gasoline": self.Gasoline,
            "HSFO":     self.HSFO,
            "Pet_coke": self.Pet_coke,
            "H2":       self.H2,
        }


class RefineryState:
    """
    État complet du bilan en cours.
    - output : produits finis (t/h)
    - pool   : flux intermédiaires en circulation (t/h)
    - input  : charge brute initiale (t/h)
    """

    def __init__(self, total_input_t_h: float):
        self.output = RefineryOutput()
        self.pool: defaultdict = defaultdict(float)
        self.input = total_input_t_h

    def pool_total(self) -> float:
        return sum(self.pool.values())

    def total(self) -> float:
        return self.output.total() + self.pool_total()

    def is_balanced(self, eps: float = 1.0) -> bool:
        return abs(self.total() - self.input) < eps

    def residual(self) -> float:
        return self.input - self.total()


# ---------------------------------------------------------------------------
# Classe abstraite
# ---------------------------------------------------------------------------

class RefineryUnits(ABC):
    def __init__(self, max_rate_kbd: float) -> None:
        self.max_rate_kbd = max_rate_kbd

    @abstractmethod
    def process_unit(self, crude, state: RefineryState) -> None:
        raise NotImplementedError

    def max_t_h(self, density: float) -> float:
        return kbd_to_t_h(self.max_rate_kbd, density)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(max={self.max_rate_kbd} kbd)"


# ---------------------------------------------------------------------------
# CDU
# ---------------------------------------------------------------------------

class CDU(RefineryUnits):
    """
    Yields CDU : lpg + naphtha + kerosene + gasoil + atm_resid = 1.0 (garanti par crudes.py)
    Produits finis : LPG, Naphtha, Kerosene, Gasoil
    Pool → atm_resid
    """

    def process_unit(self, crude, state: RefineryState) -> None:
        thru = self.max_t_h(crude.density)
        state.output.LPG      += thru * crude.lpg_yield
        state.output.Naphtha  += thru * crude.naphtha_yield
        state.output.Kerosene += thru * crude.kerosene_yield
        state.output.Gasoil   += thru * crude.gasoil_yield
        state.pool["atm_resid"] += thru * crude.atm_resid_yield


# ---------------------------------------------------------------------------
# VDU
# ---------------------------------------------------------------------------

class VDU(RefineryUnits):
    """
    Yields VDU : vgo + vac_resid = 1.0 (garanti par crudes.py)
    Surplus atm_resid (capacité dépassée) → HSFO
    Pool → vgo, vac_resid
    """

    def process_unit(self, crude, state: RefineryState) -> None:
        available = state.pool.pop("atm_resid", 0.0)
        capacity  = self.max_t_h(crude.density)
        thru      = min(available, capacity)
        surplus   = available - thru

        state.output.HSFO += surplus
        state.pool["vgo"]       += thru * crude.vgo_yield
        state.pool["vac_resid"] += thru * crude.vac_resid_yield


# ---------------------------------------------------------------------------
# FCCU
# ---------------------------------------------------------------------------

class FCCU(RefineryUnits):
    """
    Yields : LPG + Gasoline + LCO + Slurry + Coke_gas + Other = 1.0
    Affectation :
      - LPG, Gasoline → produits finis
      - Coke_gas      → H2 (approx)
      - Other         → HSFO (pertes, gaz combustible)
      - LCO, Slurry   → pool (pour FO_Blender)
    Surplus VGO non traité → HSFO
    Contrainte soufre : throughput réduit si crude trop soufré
    """

    def __init__(self, max_rate_kbd: float, sulfur_max: float = 999.0,
                 LPG: float = 0.12, Gasoline: float = 0.48, LCO: float = 0.20,
                 Slurry: float = 0.08, Coke_gas: float = 0.12, Other: float = 0.0) -> None:
        super().__init__(max_rate_kbd)
        self.sulfur_max = sulfur_max
        self.LPG      = LPG
        self.Gasoline = Gasoline
        self.LCO      = LCO
        self.Slurry   = Slurry
        self.Coke_gas = Coke_gas
        self.Other    = Other

    def set_default(self, mode: str) -> None:
        d = FCCU_DEFAULTS[mode]
        self.LPG      = d["LPG"]
        self.Gasoline = d["Gasoline"]
        self.LCO      = d["LCO"]
        self.Slurry   = d["Slurry"]
        self.Coke_gas = d["Coke_gas"]
        self.Other    = d["Other"]

    def process_unit(self, crude, state: RefineryState) -> None:
        available = state.pool.pop("vgo_fccu", 0.0)
        capacity  = self.max_t_h(crude.density)

        if crude.sulfur_pct > 0:
            sulfur_limit = capacity * (self.sulfur_max / crude.sulfur_pct)
        else:
            sulfur_limit = capacity

        thru    = min(available, capacity, sulfur_limit)
        surplus = available - thru

        state.output.HSFO     += surplus              # VGO non traité
        state.output.LPG      += thru * self.LPG
        state.output.Gasoline += thru * self.Gasoline
        state.output.H2       += thru * self.Coke_gas
        state.output.HSFO     += thru * self.Other    # pertes → HSFO
        state.pool["fccu_lco"]    += thru * self.LCO
        state.pool["fccu_slurry"] += thru * self.Slurry


# ---------------------------------------------------------------------------
# HCU
# ---------------------------------------------------------------------------

class HCU(RefineryUnits):
    """
    Yields : LPG + Naphtha + Kerosene + Diesel + Gasoil + Resid + H2_cons = 1.0
    Affectation :
      - LPG, Naphtha, Kerosene, Diesel, Gasoil → produits finis
      - Resid   → HSFO
      - H2_cons → H2 (consommation nette approximée en sortie)
    Surplus VGO non traité → HSFO
    Contrainte soufre
    """

    def __init__(self, max_rate_kbd: float, sulfur_max: float = 999.0,
                 LPG: float = 0.05, Naphtha: float = 0.20, Kerosene: float = 0.30,
                 Diesel: float = 0.38, Gasoil: float = 0.00,
                 Resid: float = 0.07, H2_cons: float = 0.00) -> None:
        super().__init__(max_rate_kbd)
        self.sulfur_max = sulfur_max
        self.LPG      = LPG
        self.Naphtha  = Naphtha
        self.Kerosene = Kerosene
        self.Diesel   = Diesel
        self.Gasoil   = Gasoil
        self.Resid    = Resid
        self.H2_cons  = H2_cons

    def set_default(self, mode: str) -> None:
        d = HCU_DEFAULTS[mode]
        self.LPG      = d["LPG"]
        self.Naphtha  = d["Naphtha"]
        self.Kerosene = d["Kerosene"]
        self.Diesel   = d["Diesel"]
        self.Gasoil   = d["Gasoil"]
        self.Resid    = d["Resid"]
        self.H2_cons  = d["H2_cons"]

    def process_unit(self, crude, state: RefineryState) -> None:
        available = state.pool.pop("vgo_hcu", 0.0)
        capacity  = self.max_t_h(crude.density)

        if crude.sulfur_pct > 0:
            sulfur_limit = capacity * (self.sulfur_max / crude.sulfur_pct)
        else:
            sulfur_limit = capacity

        thru    = min(available, capacity, sulfur_limit)
        surplus = available - thru

        state.output.HSFO     += surplus              # VGO non traité
        state.output.LPG      += thru * self.LPG
        state.output.Naphtha  += thru * self.Naphtha
        state.output.Kerosene += thru * self.Kerosene
        state.output.Diesel   += thru * self.Diesel
        state.output.Gasoil   += thru * self.Gasoil
        state.output.HSFO     += thru * self.Resid    # résidu lourd → HSFO
        state.output.H2       += thru * self.H2_cons  # H2 net (approx)


# ---------------------------------------------------------------------------
# COKER
# ---------------------------------------------------------------------------

class COKER(RefineryUnits):
    """
    Yields : LPG + Naphtha + Kerosene + Gasoil + HGO + Pet_coke = 1.0
    HGO → pool (charge supplémentaire pour HCU si disponible)
    Surplus vac_resid non traité → HSFO
    """

    def __init__(self, max_rate_kbd: float,
                 LPG: float = 0.06, Naphtha: float = 0.12, Kerosene: float = 0.10,
                 Gasoil: float = 0.38, HGO: float = 0.10, Pet_coke: float = 0.24) -> None:
        super().__init__(max_rate_kbd)
        self.LPG      = LPG
        self.Naphtha  = Naphtha
        self.Kerosene = Kerosene
        self.Gasoil   = Gasoil
        self.HGO      = HGO
        self.Pet_coke = Pet_coke

    def set_default(self, mode: str) -> None:
        d = COKER_DEFAULTS[mode]
        self.LPG      = d["LPG"]
        self.Naphtha  = d["Naphtha"]
        self.Kerosene = d["Kerosene"]
        self.Gasoil   = d["Gasoil"]
        self.HGO      = d["HGO"]
        self.Pet_coke = d["Pet_coke"]

    def process_unit(self, crude, state: RefineryState) -> None:
        available = state.pool.pop("vac_resid", 0.0)
        capacity  = self.max_t_h(crude.density)
        thru      = min(available, capacity)
        surplus   = available - thru

        state.output.HSFO     += surplus
        state.output.LPG      += thru * self.LPG
        state.output.Naphtha  += thru * self.Naphtha
        state.output.Kerosene += thru * self.Kerosene
        state.output.Gasoil   += thru * self.Gasoil
        state.output.Pet_coke += thru * self.Pet_coke
        state.pool["coker_hgo"] += thru * self.HGO   # HGO → pool pour HCU


# ---------------------------------------------------------------------------
# REFORMER
# ---------------------------------------------------------------------------

class REFORMER(RefineryUnits):
    """
    Yields : LPG + Naphtha_light + Gasoline + H2 + C1C2 + Gas = 1.0
    Affectation :
      - LPG              → produit fini
      - Gasoline + Naphtha_light → Gasoline (essence haut octane)
      - H2 + C1C2 + Gas  → H2 (sous-produit)
    Surplus naphtha non reformé → Naphtha produit fini
    """

    def __init__(self, max_rate_kbd: float,
                 LPG: float = 0.09, Naphtha_light: float = 0.10, Gasoline: float = 0.76,
                 H2: float = 0.02, C1C2: float = 0.02, Gas: float = 0.01) -> None:
        super().__init__(max_rate_kbd)
        self.LPG           = LPG
        self.Naphtha_light = Naphtha_light
        self.Gasoline      = Gasoline
        self.H2            = H2
        self.C1C2          = C1C2
        self.Gas           = Gas

    def set_default(self, mode: str) -> None:
        d = REFORMER_DEFAULTS[mode]
        self.LPG           = d["LPG"]
        self.Naphtha_light = d["Naphtha_light"]
        self.Gasoline      = d["Gasoline"]
        self.H2            = d["H2"]
        self.C1C2          = d["C1C2"]
        self.Gas           = d["Gas"]

    def process_unit(self, crude, state: RefineryState) -> None:
        available = state.pool.pop("reformer_feed", 0.0)
        if available <= 0.0:
            return

        capacity = self.max_t_h(crude.density)
        thru     = min(available, capacity)
        surplus  = available - thru

        state.output.Naphtha  += surplus                              # non reformé → Naphtha
        state.output.LPG      += thru * self.LPG
        state.output.Gasoline += thru * (self.Gasoline + self.Naphtha_light)
        state.output.H2       += thru * (self.H2 + self.C1C2 + self.Gas)


# ---------------------------------------------------------------------------
# FO_BLENDER
# ---------------------------------------------------------------------------

class FO_BLENDER(RefineryUnits):
    """
    Blende les fonds de barril (vac_tar_spill + fccu_slurry) en HSFO.
    Cutter prioritaire : LCO FCCU → fallback : Gasoil produit fini.
    fo_cut_ratio : fraction massique de cutter dans le mélange final (0.15–0.30).
    Conservation garantie : toute la charge entre en HSFO (blendé ou non).
    """

    def __init__(self, fo_cut_ratio: float = 0.20) -> None:
        super().__init__(max_rate_kbd=0.0)
        self.fo_cut_ratio = fo_cut_ratio

    def process_unit(self, crude, state: RefineryState) -> None:
        tar    = state.pool.pop("vac_tar_spill", 0.0)
        slurry = state.pool.pop("fccu_slurry",   0.0)
        feed   = tar + slurry

        if feed <= 0.0:
            return

        cutter_needed = feed * self.fo_cut_ratio / (1.0 - self.fo_cut_ratio)

        # Cutter 1 : LCO FCCU
        lco_avail    = state.pool.get("fccu_lco", 0.0)
        lco_used     = min(lco_avail, cutter_needed)
        state.pool["fccu_lco"] = lco_avail - lco_used
        remaining    = cutter_needed - lco_used

        # Cutter 2 : Gasoil produit fini
        if remaining > 0:
            go_used = min(state.output.Gasoil, remaining)
            state.output.Gasoil -= go_used
            remaining -= go_used

        # Tout le feed → HSFO (blendé ou non, la masse est conservée)
        state.output.HSFO += feed

        # LCO résiduel non utilisé comme cutter → Gasoil produit fini
        state.output.Gasoil += state.pool.pop("fccu_lco", 0.0)

