# refinery/config.py
# Configuration d'une raffinerie — unités actives et capacités

class RefineryConfig:
    def __init__(self,
                 name: str,
                 cdu_capacity_kbd: float = 100.0,
                 vdu_active: bool = True,
                 vdu_capacity_kbd: float = 100.0,
                 fccu_active: bool = True,
                 fccu_capacity_kbd: float = 50.0,
                 hcu_active: bool = True,
                 hcu_capacity_kbd: float = 50.0,
                 coker_active: bool = True,
                 coker_capacity_kbd: float = 40.0):

        self.name               = name
        self.cdu_capacity_kbd   = cdu_capacity_kbd
        self.vdu_active         = vdu_active
        self.vdu_capacity_kbd   = vdu_capacity_kbd
        self.fccu_active        = fccu_active
        self.fccu_capacity_kbd  = fccu_capacity_kbd
        self.hcu_active         = hcu_active
        self.hcu_capacity_kbd   = hcu_capacity_kbd
        self.coker_active       = coker_active
        self.coker_capacity_kbd = coker_capacity_kbd


# Configurations prédéfinies
CONFIGS = {
    "Défaut": RefineryConfig(
        name="Défaut"
    ),
    "Hydrocraquage pur": RefineryConfig(
        name="Hydrocraquage pur",
        fccu_active=False,
        hcu_capacity_kbd=100.0,
        coker_active=False,
    ),
    "Craquage catalytique pur": RefineryConfig(
        name="Craquage catalytique pur",
        fccu_capacity_kbd=100.0,
        hcu_active=False,
    ),
    "Dangote": RefineryConfig(
        name="Dangote",
        cdu_capacity_kbd=650.0,
        vdu_capacity_kbd=600.0,
        fccu_capacity_kbd=150.0,
        hcu_capacity_kbd=200.0,
        coker_capacity_kbd=120.0,
    ),
}
