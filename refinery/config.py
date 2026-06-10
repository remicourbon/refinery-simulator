"""
refinery/config.py
------------------
Configuration d'une raffinerie.

Nouveaux paramètres vs version précédente :
  - yield_mode        : "md" (moyen dégradé) ou "gm" (grande marge)
  - fccu_sulfur_max   : % soufre max accepté en charge FCCU
  - hcu_sulfur_max    : % soufre max accepté en charge HCU
  - reformer_active   : active le reformeur catalytique
  - reformer_capacity_kbd
  - fo_cut_ratio      : fraction cutter nécessaire pour le FO Blender (0.15–0.30)
"""


class RefineryConfig:
    def __init__(self,
                 name: str,

                 # CDU
                 cdu_capacity_kbd: float = 100.0,

                 # VDU
                 vdu_active: bool = True,
                 vdu_capacity_kbd: float = 100.0,

                 # FCCU
                 fccu_active: bool = True,
                 fccu_capacity_kbd: float = 50.0,
                 fccu_sulfur_max: float = 2.0,    # % soufre max en charge

                 # HCU
                 hcu_active: bool = True,
                 hcu_capacity_kbd: float = 50.0,
                 hcu_sulfur_max: float = 1.0,     # HCU plus sensible au soufre

                 # Coker
                 coker_active: bool = True,
                 coker_capacity_kbd: float = 40.0,

                 # Reformer
                 reformer_active: bool = False,
                 reformer_capacity_kbd: float = 0.0,

                 # FO Blender
                 fo_cut_ratio: float = 0.20,      # fraction cutter / (tar + cutter)

                 # Mode de yields
                 yield_mode: str = "md",          # "md" ou "gm"
                 ):

        self.name                  = name

        self.cdu_capacity_kbd      = cdu_capacity_kbd

        self.vdu_active            = vdu_active
        self.vdu_capacity_kbd      = vdu_capacity_kbd

        self.fccu_active           = fccu_active
        self.fccu_capacity_kbd     = fccu_capacity_kbd
        self.fccu_sulfur_max       = fccu_sulfur_max

        self.hcu_active            = hcu_active
        self.hcu_capacity_kbd      = hcu_capacity_kbd
        self.hcu_sulfur_max        = hcu_sulfur_max

        self.coker_active          = coker_active
        self.coker_capacity_kbd    = coker_capacity_kbd

        self.reformer_active       = reformer_active
        self.reformer_capacity_kbd = reformer_capacity_kbd

        self.fo_cut_ratio          = fo_cut_ratio
        self.yield_mode            = yield_mode


# ---------------------------------------------------------------------------
# Configurations prédéfinies
# ---------------------------------------------------------------------------

CONFIGS = {

    "Défaut": RefineryConfig(
        name="Défaut",
        reformer_active=True,
        reformer_capacity_kbd=30.0,
    ),

    "Hydrocraquage pur": RefineryConfig(
        name="Hydrocraquage pur",
        fccu_active=False,
        hcu_capacity_kbd=100.0,
        hcu_sulfur_max=0.5,
        coker_active=False,
        reformer_active=True,
        reformer_capacity_kbd=30.0,
        yield_mode="gm",
    ),

    "Craquage catalytique pur": RefineryConfig(
        name="Craquage catalytique pur",
        fccu_capacity_kbd=100.0,
        fccu_sulfur_max=3.0,
        hcu_active=False,
        reformer_active=True,
        reformer_capacity_kbd=30.0,
        yield_mode="gm",
    ),

    "Dangote": RefineryConfig(
        name="Dangote",
        cdu_capacity_kbd=650.0,
        vdu_capacity_kbd=600.0,
        fccu_capacity_kbd=150.0,
        fccu_sulfur_max=2.5,
        hcu_capacity_kbd=200.0,
        hcu_sulfur_max=1.5,
        coker_capacity_kbd=120.0,
        reformer_active=True,
        reformer_capacity_kbd=80.0,
        fo_cut_ratio=0.25,
        yield_mode="md",
    ),

    "Raffinerie simple (pas de conversion)": RefineryConfig(
        name="Raffinerie simple (pas de conversion)",
        vdu_active=False,
        fccu_active=False,
        hcu_active=False,
        coker_active=False,
        reformer_active=False,
    ),

    "Maximisation distillats (mode grande marge)": RefineryConfig(
        name="Maximisation distillats (mode grande marge)",
        fccu_active=False,
        hcu_capacity_kbd=80.0,
        hcu_sulfur_max=0.5,
        coker_active=True,
        coker_capacity_kbd=50.0,
        reformer_active=True,
        reformer_capacity_kbd=40.0,
        fo_cut_ratio=0.15,
        yield_mode="gm",
    ),
}
