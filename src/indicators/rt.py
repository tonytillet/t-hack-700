# src/indicators/rt.py
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Iterable, Tuple, Dict, Optional

# SciPy pour la CDF Gamma (poids de l'intervalle sériel)
from scipy.stats import gamma

# ---------- Utils intervalle sériel (Gamma discrétisée) ----------
def _si_weights(S: int, mean: float, sd: float) -> np.ndarray:
    """
    Poids w_s (s=1..S) pour l'intervalle sériel ~ Gamma discrétisée.
    mean/sd doivent être dans LA MÊME unité que l'incidence (jour ou semaine).
    """
    # shape-scale
    k = (mean / sd) ** 2
    theta = (sd ** 2) / mean
    xs = np.arange(1, S + 1, dtype=float)
    cdf = gamma.cdf(xs, a=k, scale=theta)
    cdf_prev = gamma.cdf(xs - 1, a=k, scale=theta)
    w = (cdf - cdf_prev)
    w = w / w.sum()
    return w

def _cori_rt(inc: pd.Series, w: np.ndarray, min_denom: float = 1.0) -> pd.Series:
    """
    Méthode de Cori : R_t = I_t / sum_{s=1..S} I_{t-s} * w_s
    - incidence inc: Série temporelle (>=0)
    - w: poids de l'intervalle sériel
    - min_denom: garde-fou pour éviter des explosions lorsque l'incidence est quasi nulle
    """
    I = inc.fillna(0).astype(float).values
    S = len(w)
    Rt = np.full_like(I, np.nan, dtype=float)
    for t in range(S, len(I)):
        denom = float(np.sum(I[t - np.arange(1, S + 1)] * w))
        if denom >= min_denom:
            Rt[t] = I[t] / denom
    return pd.Series(Rt, index=inc.index)

def _is_weekly(df: pd.DataFrame) -> bool:
    """Détecte si la granularité est hebdomadaire (delta médian >= 6 jours)."""
    if 'date' not in df.columns:
        return True
    deltas = df.sort_values('date').groupby('region')['date'].apply(lambda s: s.diff().dt.days.dropna())
    med = deltas.median() if len(deltas) else 7.0
    return bool(med >= 6.0)

# ---------- API publique ----------
def compute_rt_avg_from_data(
    full_df: pd.DataFrame,
    inc_columns: Iterable[str] = ('cas_sentinelles', 'urgences_grippe'),
    si_mean_days: float = 2.6,
    si_sd_days: float = 1.5,
    si_horizon: int = 10,
    min_denom: float = 1.0,
) -> float:
    """
    Calcule R_t (Cori) sur TOUTE la série 'full_df' (par région),
    puis retourne la MOYENNE NATIONALE de la dernière valeur R_t par région.
    """
    last_per_region = compute_rt_last_by_region(
        full_df, inc_columns, si_mean_days, si_sd_days, si_horizon, min_denom
    )
    vals = [v for v in last_per_region.values() if pd.notna(v)]
    return float(np.nanmean(vals)) if len(vals) else float('nan')

def compute_rt_last_by_region(
    full_df: pd.DataFrame,
    inc_columns: Iterable[str] = ('cas_sentinelles', 'urgences_grippe'),
    si_mean_days: float = 2.6,
    si_sd_days: float = 1.5,
    si_horizon: int = 10,
    min_denom: float = 1.0,
) -> Dict[str, float]:
    """
    Retourne un dict {region -> R_t courant (dernier point)}.
    Utile pour cartes ou KPIs par région.
    """
    if full_df is None or full_df.empty:
        return {}

    df = full_df.copy()
    inc_col: Optional[str] = next((c for c in inc_columns if c in df.columns), None)
    if inc_col is None:
        return {}

    df = df[['region', 'date', inc_col]].dropna(subset=['region', 'date']).sort_values(['region', 'date'])

    # Choix de l'unité pour l'intervalle sériel
    if _is_weekly(df):
        mean, sd, S = si_mean_days / 7.0, si_sd_days / 7.0, max(6, si_horizon - 2)
    else:
        mean, sd, S = si_mean_days, si_sd_days, si_horizon

    w = _si_weights(S=S, mean=mean, sd=sd)

    out: Dict[str, float] = {}
    for reg, g in df.groupby('region', dropna=False):
        rt = _cori_rt(g[inc_col], w=w, min_denom=min_denom)
        out[str(reg)] = float(rt.dropna().iloc[-1]) if rt.notna().any() else float('nan')

    return out
