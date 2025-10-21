# src/indicators/severity.py
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Iterable

def compute_severity_last_by_region(
    full_df: pd.DataFrame,
    hosp_col: str = "urgences_grippe",
    inc_candidates: Iterable[str] = ("cas_sentinelles", "urgences_grippe"),
) -> pd.DataFrame:
    """
    Retourne un DF [region, G] avec G = (urgences / cas) * 100 à la DERNIÈRE date par région.
    - hosp_col : colonne des hospitalisations/urgences
    - inc_candidates : colonnes candidates pour les cas (on prend la 1ère présente)
    """
    if full_df is None or full_df.empty:
        return pd.DataFrame(columns=["region", "G"])

    df = full_df.sort_values("date").groupby("region").tail(1).copy()

    inc_col = next((c for c in inc_candidates if c in df.columns), None)
    if inc_col is None or hosp_col not in df.columns:
        return pd.DataFrame(columns=["region", "G"])

    denom = df[inc_col].replace(0, np.nan)  # évite division par 0
    G = (df[hosp_col] / denom * 100.0).astype(float)
    out = df[["region"]].copy()
    out["G"] = G.fillna(0.0).values
    return out

def compute_severity_avg_from_data(full_df: pd.DataFrame) -> float:
    """
    Moyenne nationale du taux de gravité (dernière valeur par région).
    """
    per_region = compute_severity_last_by_region(full_df)
    return float(per_region["G"].mean()) if not per_region.empty else float("nan")
