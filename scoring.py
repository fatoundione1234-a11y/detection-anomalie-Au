# ============================================================
# GeoSat Kédougou — utils/scoring.py
# Modèle de scoring du potentiel aurifère
# ============================================================

import numpy as np
import pandas as pd
from typing import Optional
import yaml
from pathlib import Path


CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_weights() -> dict:
    """Charge les poids du modèle depuis config.yaml."""
    try:
        with open(CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
        return cfg["scoring"]["weights"]
    except Exception:
        return {
            "intensite": 0.30, "hydrothermal": 0.25,
            "alteration": 0.20, "faille_dist": 0.15, "band_ratio": 0.10,
        }


def compute_score(row: pd.Series, weights: Optional[dict] = None) -> float:
    """
    Calcule le score de potentiel aurifère (0–100) pour une zone.

    Modèle pondéré :
        Score = intensité×0.30 + hydrothermal×0.25 + altération×0.20
              + proximitéFaille×0.15 + ratioSWIR×0.10

    Args:
        row:     Ligne pandas avec colonnes: intensite, hydrothermal,
                 alteration, faille_dist, band_ratio
        weights: Dict de poids personnalisés (optionnel)

    Returns:
        Score float [0, 100]
    """
    w = weights or load_weights()

    prox_faille = max(0.0, 100.0 - float(row["faille_dist"]) * 15.0)
    swir_norm   = min(100.0, (float(row["band_ratio"]) / 3.5) * 100.0)

    score = (
        float(row["intensite"])    * w.get("intensite",    0.30) +
        float(row["hydrothermal"]) * w.get("hydrothermal", 0.25) +
        float(row["alteration"])   * w.get("alteration",   0.20) +
        prox_faille                * w.get("faille_dist",  0.15) +
        swir_norm                  * w.get("band_ratio",   0.10)
    )
    return round(score, 1)


def classify_priority(score: float, seuils: Optional[dict] = None) -> str:
    """
    Classifie la priorité d'une zone selon son score.

    Args:
        score:  Score IA [0, 100]
        seuils: Dict avec clés 'haute_priorite', 'moyenne_priorite', 'faible_priorite'

    Returns:
        Priorité parmi : HAUTE | MOYENNE | FAIBLE | NULLE
    """
    try:
        with open(CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
        s = seuils or cfg["scoring"]["seuils"]
    except Exception:
        s = {"haute_priorite": 80, "moyenne_priorite": 55, "faible_priorite": 30}

    if score >= s["haute_priorite"]:
        return "HAUTE"
    elif score >= s["moyenne_priorite"]:
        return "MOYENNE"
    elif score >= s["faible_priorite"]:
        return "FAIBLE"
    else:
        return "NULLE"


def rank_zones(df: pd.DataFrame, weights: Optional[dict] = None) -> pd.DataFrame:
    """
    Calcule et ajoute les colonnes score_ia et priorite_ia au DataFrame.

    Args:
        df:      DataFrame des zones (doit avoir les colonnes requises)
        weights: Poids personnalisés (optionnel)

    Returns:
        DataFrame enrichi trié par score décroissant
    """
    w = weights or load_weights()
    df = df.copy()
    df["score_ia"]    = df.apply(lambda r: compute_score(r, w), axis=1)
    df["priorite_ia"] = df["score_ia"].apply(classify_priority)
    return df.sort_values("score_ia", ascending=False).reset_index(drop=True)


def get_feature_importance(weights: Optional[dict] = None) -> pd.DataFrame:
    """
    Retourne un DataFrame des indicateurs avec leur poids normalisé en %.

    Returns:
        DataFrame avec colonnes: indicateur, poids, poids_pct, couleur
    """
    w = weights or load_weights()
    total = sum(w.values())
    colors = {
        "intensite":    "#f59e0b",
        "hydrothermal": "#fb923c",
        "alteration":   "#e879f9",
        "faille_dist":  "#a78bfa",
        "band_ratio":   "#38bdf8",
    }
    labels = {
        "intensite":    "Intensité anomalie",
        "hydrothermal": "Indice hydrothermal",
        "alteration":   "Altération spectrale",
        "faille_dist":  "Proximité faille",
        "band_ratio":   "Ratio SWIR",
    }
    return pd.DataFrame([{
        "indicateur": labels.get(k, k),
        "poids":      v,
        "poids_pct":  round(v / total * 100, 1),
        "couleur":    colors.get(k, "#94a3b8"),
    } for k, v in w.items()]).sort_values("poids", ascending=False)


def generate_recommendation(zone: pd.Series) -> str:
    """
    Génère une recommandation textuelle basée sur les métriques de la zone.

    Args:
        zone: Ligne pandas d'une zone

    Returns:
        Texte de recommandation
    """
    if zone["type"] == "aurifere":
        return (
            f"Zone à fort potentiel aurifère (score IA : {zone.get('score_ia','N/A')}/100). "
            f"L'altération hydrothermale de {zone['alteration']}% combinée à une "
            f"proximité de faille de {zone['faille_dist']} km constitue un contexte "
            f"favorable aux minéralisations. Prospection géochimique sol recommandée "
            f"en priorité, suivie de sondages RC/DD dans un délai de 3 à 6 mois."
        )
    elif zone["type"] == "structure":
        return (
            f"Structure géologique d'intérêt structural. Le ratio SWIR de {zone['band_ratio']} "
            f"indique une altération modérée à forte. Une cartographie structurale détaillée "
            f"et des relevés de terrain permettraient d'affiner l'évaluation du potentiel "
            f"en bordure des failles identifiées."
        )
    else:
        return (
            f"Zone à faible potentiel selon l'analyse spectrale. Le NDVI de {zone['ndvi']} "
            f"indique une couverture végétale ou un sol peu altéré, limitant la détection "
            f"d'anomalies aurifères. Réévaluation recommandée en période de saison sèche "
            f"(novembre–avril) pour une meilleure fenêtre spectrale."
        )
