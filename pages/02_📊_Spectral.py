# ============================================================
# GeoSat Kédougou — utils/spectral.py
# Calcul des indices spectraux de télédétection
# ============================================================

import numpy as np
import pandas as pd
from typing import Union, Optional


# ─────────────────────────────────────────────────────────────
# INDICES CLASSIQUES
# ─────────────────────────────────────────────────────────────

def compute_ndvi(b4: np.ndarray, b8: np.ndarray) -> np.ndarray:
    """
    Normalized Difference Vegetation Index.
    NDVI = (B8 - B4) / (B8 + B4)

    Interprétation Kédougou :
    - NDVI < 0.1  → sol nu / altéré (favorable détection aurifère)
    - NDVI > 0.4  → végétation dense (masque anomalies)

    Args:
        b4: Bande rouge Sentinel-2 (665nm)
        b8: Bande NIR Sentinel-2 (842nm)

    Returns:
        Raster NDVI [-1, 1]
    """
    denom = b8 + b4
    denom = np.where(denom == 0, np.nan, denom)
    return (b8 - b4) / denom


def compute_ndwi(b3: np.ndarray, b8: np.ndarray) -> np.ndarray:
    """
    Normalized Difference Water Index.
    NDWI = (B3 - B8) / (B3 + B8)
    Détecte humidité et zones hydromorphes.
    """
    denom = b3 + b8
    denom = np.where(denom == 0, np.nan, denom)
    return (b3 - b8) / denom


def compute_swir_ratio(b11: np.ndarray, b12: np.ndarray) -> np.ndarray:
    """
    Ratio SWIR — Indicateur d'altération hydrothermale.
    Ratio = B11 / B12

    Interprétation :
    - Ratio > 2.5 → forte altération hydrothermale aurifère
    - Ratio < 1.5 → roche fraîche, peu altérée

    Args:
        b11: Bande SWIR1 Sentinel-2 (1610nm)
        b12: Bande SWIR2 Sentinel-2 (2190nm)
    """
    denom = np.where(b12 == 0, np.nan, b12)
    return b11 / denom


def compute_clay_index(b11: np.ndarray, b8: np.ndarray) -> np.ndarray:
    """
    Clay Minerals Index — Détection argiles (kaolinite, illite).
    CI = B11 / B8
    """
    denom = np.where(b8 == 0, np.nan, b8)
    return b11 / denom


def compute_ferrous_oxide(b11: np.ndarray, b8a: np.ndarray) -> np.ndarray:
    """
    Ferrous Oxide Index — Oxydes de fer (limonite, goethite).
    FOI = B11 / B8A
    Marqueur clé des gossan et chapeaux de fer aurifères.
    """
    denom = np.where(b8a == 0, np.nan, b8a)
    return b11 / denom


def compute_gossan_index(b4: np.ndarray, b2: np.ndarray) -> np.ndarray:
    """
    Gossan Index — Zones gossanisées (chapeaux de fer).
    GI = B4 / B2
    Les gossans sont des indicateurs de surface de minéralisations sulfurées.
    """
    denom = np.where(b2 == 0, np.nan, b2)
    return b4 / denom


def compute_alteration_index(b4: np.ndarray, b8: np.ndarray,
                              b11: np.ndarray, b12: np.ndarray) -> np.ndarray:
    """
    Indice d'altération composite (0-100).
    Combine NDVI inverse et ratio SWIR.
    """
    ndvi = compute_ndvi(b4, b8)
    swir = compute_swir_ratio(b11, b12)
    # Score normalisé
    ndvi_score = np.clip((1 - ndvi) * 50, 0, 50)
    swir_score = np.clip((swir / 3.5) * 50, 0, 50)
    return ndvi_score + swir_score


# ─────────────────────────────────────────────────────────────
# PROFIL SPECTRAL
# ─────────────────────────────────────────────────────────────

def get_spectral_profile(bands_dict: dict) -> pd.DataFrame:
    """
    Calcule tous les indices spectraux pour un ensemble de bandes.

    Args:
        bands_dict: dict avec clés 'B2','B3','B4','B8','B8A','B11','B12'
                    Valeurs : scalaires (float) ou arrays numpy

    Returns:
        DataFrame avec tous les indices calculés
    """
    b2  = bands_dict.get("B2",  0)
    b3  = bands_dict.get("B3",  0)
    b4  = bands_dict.get("B4",  0)
    b8  = bands_dict.get("B8",  0)
    b8a = bands_dict.get("B8A", 0)
    b11 = bands_dict.get("B11", 0)
    b12 = bands_dict.get("B12", 0)

    indices = {
        "NDVI":           compute_ndvi(b4, b8),
        "NDWI":           compute_ndwi(b3, b8),
        "SWIR_Ratio":     compute_swir_ratio(b11, b12),
        "Clay_Index":     compute_clay_index(b11, b8),
        "Ferrous_Oxide":  compute_ferrous_oxide(b11, b8a) if b8a != 0 else None,
        "Gossan_Index":   compute_gossan_index(b4, b2),
        "Alteration_Idx": compute_alteration_index(b4, b8, b11, b12),
    }
    return pd.DataFrame([{k: float(v) if v is not None else None
                          for k, v in indices.items()}])


def interpret_ndvi(ndvi: float) -> str:
    """Retourne l'interprétation géologique du NDVI."""
    if ndvi < -0.05:
        return "Sol très dénudé / fortement altéré — très favorable"
    elif ndvi < 0.1:
        return "Sol peu végétalisé / altéré — favorable"
    elif ndvi < 0.3:
        return "Végétation clairsemée — modérément favorable"
    elif ndvi < 0.5:
        return "Végétation modérée — peu favorable"
    else:
        return "Dense végétation — masque les anomalies spectrales"


def interpret_swir(ratio: float) -> str:
    """Retourne l'interprétation géologique du ratio SWIR."""
    if ratio > 3.0:
        return "Très forte altération hydrothermale — cible prioritaire"
    elif ratio > 2.5:
        return "Forte altération hydrothermale — favorable"
    elif ratio > 1.8:
        return "Altération modérée — à investiguer"
    else:
        return "Roche peu altérée — faible potentiel"
