#!/usr/bin/env python3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

LEVEL_MAP = {
    '🔴 Critique': ('critique', 80, 1000),
    '🟠 Élevé': ('eleve', 60, 79.999),
    '🟡 Modéré': ('modere', 40, 59.999),
    '🟢 Faible': ('faible', 0, 39.999),
}

PERIOD_OPTIONS = {
    '7 derniers jours': 7,
    '14 derniers jours': 14,
    '30 derniers jours': 30,
    '90 derniers jours': 90,
    'Toute la période': None,
}

def filter_by_level(df: pd.DataFrame, level_label: str) -> pd.DataFrame:
    if df is None or len(df) == 0 or level_label == 'Tous' or 'alert_score' not in df.columns:
        return df
    _, lo, hi = LEVEL_MAP.get(level_label, ('all', None, None))
    if lo is None:
        return df
    return df[(df['alert_score'] >= lo) & (df['alert_score'] <= hi)]


def filter_by_period(df: pd.DataFrame, period_label: str) -> pd.DataFrame:
    if df is None or len(df) == 0 or period_label not in PERIOD_OPTIONS or 'date' not in df.columns:
        return df
    days = PERIOD_OPTIONS[period_label]
    if days is None:
        return df
    cutoff = pd.to_datetime(datetime.now() - timedelta(days=days))
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    return df[df['date'] >= cutoff]


def regions_in_alert_count(df: pd.DataFrame, threshold: float = 60.0) -> int:
    if df is None or len(df) == 0 or 'alert_score' not in df.columns:
        return 0
    latest = df.groupby('region').last().reset_index()
    return int((latest.get('alert_score', pd.Series([0])) >= threshold).sum())


def apply_filters(df: pd.DataFrame, level_label: str, period_label: str) -> pd.DataFrame:
    dfp = filter_by_period(df, period_label)
    return filter_by_level(dfp, level_label)
