# data/prices.py
# Prix réels depuis l'API EIA + différentiels fixes pour les produits non disponibles
#
# Sources :
#   - Brent    : EIA spot (EPCBRENT) — prix officiel
#   - Diesel   : EIA spot (EPD2DC)   — Los Angeles CARB Diesel
#   - Kerosene : EIA spot (EPJK)     — Gulf Coast Jet Fuel
#   - Autres   : différentiel fixe sur le Brent (moyennes historiques)

import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# 1 gallon = 42 barils → prix en $/gallon × 42 = $/bbl
GAL_TO_BBL = 42


def _get_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets.get("API_KEY_EIA") or os.getenv("API_KEY_EIA")
    except Exception:
        return os.getenv("API_KEY_EIA")


def _get_spot_price(product_code: str, length: int = 1) -> pd.DataFrame:
    """
    Récupère les prix spot EIA pour un produit donné.
    Retourne un DataFrame avec colonnes [date, prix].
    """
    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    params = {
        "api_key":              _get_api_key(),
        "frequency":            "daily",
        "data[0]":              "value",
        "facets[product][]":    product_code,
        "sort[0][column]":      "period",
        "sort[0][direction]":   "desc",
        "length":               length,
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data["response"]["data"])
    df["period"] = pd.to_datetime(df["period"])
    df["value"]  = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    df = df.sort_values("period")
    return df[["period", "value"]].rename(columns={"period": "date", "value": "prix"})


# ---------------------------------------------------------------------------
# Prix spot actuels
# ---------------------------------------------------------------------------

def get_prix_brent() -> float:
    """Prix spot Brent actuel en $/bbl — source EIA."""
    df = _get_spot_price("EPCBRENT", length=1)
    return round(float(df["prix"].iloc[-1]), 2)


def get_prix_produits_eia() -> dict:
    """
    Prix actuels de tous les produits raffinés.

    EIA (prix spot réels) :
      - Diesel   : Los Angeles CARB Diesel
      - Kerosene : Gulf Coast Jet Fuel

    Différentiels fixes sur le Brent (moyennes historiques) :
      - Gasoline : Brent + 20$
      - Gasoil   : Brent + 12$
      - Naphtha  : Brent -  8$
      - LPG      : Brent - 10$
      - HSFO     : Brent - 15$
      - Pet_coke : Brent - 55$
    """
    brent = get_prix_brent()

    # Produits disponibles sur EIA en $/gallon
    produits_eia = {
        "Diesel":   ("EPD2DC", GAL_TO_BBL),   # Los Angeles CARB Diesel
        "Kerosene": ("EPJK",   GAL_TO_BBL),   # Gulf Coast Jet Fuel
    }

    prix = {}
    for produit, (code, facteur) in produits_eia.items():
        try:
            df = _get_spot_price(code, length=1)
            prix[produit] = round(float(df["prix"].iloc[-1]) * facteur, 2)
        except Exception:
            # Fallback différentiel fixe si l'API échoue
            prix[produit] = round(brent + 12.0, 2)

    # Différentiels fixes sur le Brent
    prix["Gasoline"] = round(brent + 20.0, 2)
    prix["Gasoil"]   = round(brent + 12.0, 2)
    prix["Naphtha"]  = round(brent -  8.0, 2)
    prix["LPG"]      = round(brent - 10.0, 2)
    prix["HSFO"]     = round(brent - 15.0, 2)
    prix["Pet_coke"] = round(brent - 55.0, 2)

    return prix


def get_prix_bruts() -> dict:
    """
    Prix actuels des 4 bruts.
    Brent : EIA spot.
    Autres : différentiel fixe sur le Brent.
    """
    brent = get_prix_brent()
    return {
        "Brent":        round(brent,        2),
        "Urals":        round(brent - 15.0, 2),
        "Arab Light":   round(brent -  4.0, 2),
        "Sahara Blend": round(brent +  3.0, 2),
    }


# ---------------------------------------------------------------------------
# Historiques
# ---------------------------------------------------------------------------

def get_historique_brent(jours: int = 365) -> pd.DataFrame:
    """Historique du prix Brent sur N jours — source EIA."""
    return _get_spot_price("EPCBRENT", length=jours)


def get_historique_produit(produit: str, jours: int = 365) -> pd.DataFrame:
    """
    Historique d'un produit raffiné sur N jours.
    Disponible pour Diesel et Kerosene via EIA.
    """
    codes = {
        "Diesel":   ("EPD2DC", GAL_TO_BBL),
        "Kerosene": ("EPJK",   GAL_TO_BBL),
    }

    if produit not in codes:
        raise ValueError(f"{produit} non disponible sur EIA — utilise un différentiel fixe")

    code, facteur = codes[produit]
    df = _get_spot_price(code, length=jours)
    df["prix"] = df["prix"] * facteur
    return df

