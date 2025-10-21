# src/indicators/severity.py
from __future__ import annotations
import numpy as np
import pandas as pd

def compute_severity_avg(latest: pd.DataFrame) -> float:
    """
    Taux de gravité (identique au code actuel):
      G = (urgences_grippe / cas_sentinelles) × 100
    Retour: moyenne (float, en %)
    """
    if latest is None or latest.empty:
        return 0.0

    vals = []
    for _, row in latest.iterrows():
        urg = (row.get("urgences_grippe", 0) or 0)
        cas = (row.get("cas_sentinelles", 0) or 0)
        vals.append((urg / max(cas, 1)) * 100.0)
    return float(np.mean(vals)) if vals else 0.0
