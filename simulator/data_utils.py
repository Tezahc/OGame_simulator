import pandas as pd
import numpy as np
from typing import Any, List


def create_dataframe_like(df_template: pd.DataFrame, n_rows: int, fill_value: Any = None) -> pd.DataFrame:
    """Create a new DataFrame with the same columns as `df_template`.

    Parameters
    - df_template: DataFrame whose columns (and dtypes when possible) will be used.
    - n_rows: number of rows for the returned DataFrame (must be >= 0).
    - fill_value: value to fill each cell with. If None, cells will be left as missing.

    Returns
    - pd.DataFrame with shape (n_rows, len(df_template.columns)).
    """
    if n_rows < 0:
        raise ValueError("n_rows must be >= 0")

    cols = df_template.columns
    # create empty frame with correct columns and integer index
    df = pd.DataFrame(index=range(n_rows), columns=cols)

    if fill_value is not None:
        df.loc[:] = fill_value

    # try to preserve dtypes from template where possible
    try:
        dtype_map = {col: dt for col, dt in df_template.dtypes.items()}
        df = df.astype(dtype_map, copy=False, errors="ignore")
    except Exception:
        # if anything goes wrong, return the DataFrame as-is
        return df

    return df

def replicate_rows(df: pd.DataFrame, counts: List[int]) -> pd.DataFrame:
    """Replicate rows of `df` according to `counts`.

    Parameters
    - df: source DataFrame
    - counts: sequence of non-negative integers with the same length as `df`.

    Returns
    - A new DataFrame where each row i from `df` appears `counts[i]` times.
      Rows with a count of 0 are omitted. The result has a fresh RangeIndex.
    """
    if len(counts) != len(df):
        raise ValueError("counts must have the same length as df")

    arr = np.asarray(counts, dtype=np.int64)
    if (arr < 0).any():
        raise ValueError("counts must contain non-negative integers")
    
    if df.shape[0] == 0:
        return df.copy()

    repeated_idx = np.repeat(df.index.values, arr)
    if repeated_idx.size == 0:
        return df.iloc[0:0].copy()

    result = df.loc[repeated_idx].reset_index(drop=True)
    return result

def compute_shield(df_side: pd.DataFrame):
    df = df_side.copy()
    df["dmg_shield"] = (np.floor(100 * df.attaque_A / df.bouclier_D) * df.bouclier_D // 100).astype(int)
    df = df.sort_values(by=["cible", "tireur"])[["tireur", "nom_A", "attaque_A", "cible", "nom_D", "bouclier_D", "structure_D", "dmg_shield"]]

    df["shield_aft_hit"] = df.bouclier_D - df.groupby("cible")["dmg_shield"].cumsum()

    df["shield_bef_hit"] = df.groupby("cible")["shield_aft_hit"].shift(1).fillna(df.bouclier_D).astype(int)

    is_overkill = df.shield_aft_hit <= 0
    is_hs = df.shield_bef_hit <= 0
    
    return df