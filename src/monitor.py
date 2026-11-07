import numpy as np
import pandas as pd


def psi(reference, new, bins=10):
    reference = pd.Series(reference).dropna()
    new = pd.Series(new).dropna()

    # group edges come from the training (reference) data only
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf

    ref_pct = np.histogram(reference, bins=edges)[0] / len(reference)
    new_pct = np.histogram(new, bins=edges)[0] / len(new)

    # avoid log(0) and division by zero
    ref_pct = np.clip(ref_pct, 1e-4, None)
    new_pct = np.clip(new_pct, 1e-4, None)

    return float(np.sum((new_pct - ref_pct) * np.log(new_pct / ref_pct)))


def psi_status(value):
    if value < 0.10:
        return 'stable'
    if value < 0.25:
        return 'watch'
    return 'retrain'
