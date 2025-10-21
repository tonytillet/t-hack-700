# src/indicators/sc.py
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Optional, Iterable
from .rt import compute_rt_last_by_region  # Rₜ courant par région

def _minmax(s: pd.Series) -> pd.Series:
    vmin, vmax = np.nanmin(s.values), np.nanmax(s.values)
    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmax - vmin < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - vmin) / (vmax - vmin)

def _rt_logistic(x: pd.Series | float, k: float = 4.0) -> pd.Series | float:
    # Sigmoïde centrée sur 1 (0.5 au seuil épidémique)
    if isinstance(x, (float, int)):
        return float(1.0 / (1.0 + np.exp(-k * (float(x) - 1.0))))
    x = x.astype(float)
    return 1.0 / (1.0 + np.exp(-k * (x - 1.0)))

def compute_sc_avg_from_data(
    full_df: pd.DataFrame,
    inc_columns: Iterable[str] = ('cas_sentinelles', 'urgences_grippe'),
    k: float = 4.0,
) -> float:
    """
    SC (0–1) = sigmoïde(Rₜ, k) × densité_normalisée.
    - Utilise la DERNIÈRE valeur par région (Rₜ + densité de la dernière ligne).
    - Retourne la moyenne nationale (float).
    """
    if full_df is None or full_df.empty:
        return float('nan')

    # 1) Rₜ courant par région (Cori)
    rt_last: Dict[str, float] = compute_rt_last_by_region(full_df, inc_columns=inc_columns)

    # 2) Densité normalisée sur la DERNIÈRE ligne par région
    g = full_df.sort_values('date').groupby('region').tail(1).copy()
    if 'densite' in g.columns:
        dens_norm = _minmax(g['densite'])
    else:
        dens_norm = pd.Series(1.0, index=g.index)

    # 3) Aligner Rₜ sur les régions et calculer SC
    rt_aligned = pd.Series([rt_last.get(str(r), np.nan) for r in g['region']], index=g.index)
    rt_sig = _rt_logistic(rt_aligned, k=k)
    sc = (rt_sig * dens_norm).clip(0, 1)

    return float(sc.mean()) if len(sc) else float('nan')


# (Optionnel) Série par région si tu veux une carte/tablaeu
def compute_sc_last_by_region(
    full_df: pd.DataFrame,
    inc_columns: Iterable[str] = ('cas_sentinelles', 'urgences_grippe'),
    k: float = 4.0,
) -> pd.DataFrame:
    """
    Retourne un DataFrame [region, SC] avec SC dans [0,1] (dernière valeur par région).
    """
    rt_last = compute_rt_last_by_region(full_df, inc_columns=inc_columns)
    g = full_df.sort_values('date').groupby('region').tail(1).copy()

    if 'densite' in g.columns:
        dens_norm = _minmax(g['densite'])
    else:
        dens_norm = pd.Series(1.0, index=g.index)

    rt_aligned = pd.Series([rt_last.get(str(r), np.nan) for r in g['region']], index=g.index)
    rt_sig = _rt_logistic(rt_aligned, k=k)
    sc = (rt_sig * dens_norm).clip(0, 1)

    out = g[['region']].copy()
    out['SC'] = sc.values
    return out
