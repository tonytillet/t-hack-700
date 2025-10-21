# src/indicators/lumen_score.py
from __future__ import annotations
import numpy as np
import pandas as pd
from .rt import compute_rt_avg_from_data

def compute_lumen_score_avg(latest: pd.DataFrame) -> float:
    """
    Reproduit la formule actuelle du LUMEN-Score (moyenne sur régions):
      iae         = (google_trends_grippe + wiki_grippe_views) / 100
      r0_norm     = min(1, max(0, (avg_r0 - 0.8) / 1.2))
      v           = vaccination_2024 / 100 (default 50%)
      d_norm      = min(1, population_totale / 10_000_000)
      climat_norm = 0.5 (constante)
      LS_region   = (0.30*iae + 0.25*r0_norm + 0.20*(1 - v) + 0.15*d_norm + 0.10*climat) * 100
    Retour: moyenne des LS par région (float, /100 déjà appliqué)
    """
    if latest is None or latest.empty:
        return 0.0

    avg_r0 = compute_rt_avg_from_data(latest)
    r0_norm = min(1.0, max(0.0, (avg_r0 - 0.8) / 1.2))
    climat_norm = 0.5

    ls_vals = []
    for _, row in latest.iterrows():
        trends = (row.get("google_trends_grippe", 0) or 0)
        wiki = (row.get("wiki_grippe_views", 0) or 0)
        iae = (trends + wiki) / 100.0

        v = (row.get("vaccination_2024", 50) or 50) / 100.0
        d_norm = min(1.0, (row.get("population_totale", 100_000) or 100_000) / 10_000_000.0)

        ls = (0.30 * iae + 0.25 * r0_norm + 0.20 * (1.0 - v) + 0.15 * d_norm + 0.10 * climat_norm) * 100.0
        ls_vals.append(ls)

    return float(np.mean(ls_vals)) if ls_vals else 0.0
