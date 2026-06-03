"""Build training-aligned features from raw sensor readings (single recording)."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from features.DataTransformation import LowPassFilter, PrincipalComponentAnalysis
from features.TemporalAbstraction import NumericalAbstraction
from features.FrequencyAbstraction import FourierTransformation

PREDICTOR_COLUMNS = ["acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"]
FS = int(1000 / 200)
TEMPORAL_WS = int(1000 / 200)
FREQ_WS = int(2800 / 200)


def engineer_features_from_raw(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the same feature pipeline as build_features.py on one continuous recording.
    Returns a dataframe with engineered columns (multiple rows; use last row for predict).
    """
    missing = [c for c in PREDICTOR_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing sensor columns: {missing}")

    min_rows = FREQ_WS + 2
    if len(df) < min_rows:
        raise ValueError(
            f"Need at least {min_rows} sensor rows for feature extraction; got {len(df)}."
        )

    data = df[PREDICTOR_COLUMNS].copy()
    for col in PREDICTOR_COLUMNS:
        data[col] = data[col].interpolate().bfill().ffill()

    data["set"] = 1

    low_pass = LowPassFilter()
    processed = data.copy()
    for col in PREDICTOR_COLUMNS:
        processed = low_pass.low_pass_filter(processed, col, FS, 1, order=5)
        processed[col] = processed[f"{col}_lowpass"]
        del processed[f"{col}_lowpass"]

    pca = PrincipalComponentAnalysis()
    processed = pca.apply_pca(processed, PREDICTOR_COLUMNS, 3)

    processed["acc_r"] = np.sqrt(
        processed["acc_x"] ** 2 + processed["acc_y"] ** 2 + processed["acc_z"] ** 2
    )
    processed["gyro_r"] = np.sqrt(
        processed["gyro_x"] ** 2 + processed["gyro_y"] ** 2 + processed["gyro_z"] ** 2
    )

    num_abs = NumericalAbstraction()
    cols = PREDICTOR_COLUMNS + ["acc_r", "gyro_r"]
    for col in cols:
        processed = num_abs.abstract_numerical(processed, [col], TEMPORAL_WS, "mean")
        processed = num_abs.abstract_numerical(processed, [col], TEMPORAL_WS, "std")

    processed = processed.reset_index(drop=True)
    freq_abs = FourierTransformation()
    processed = freq_abs.abstract_frequency(processed, cols, FREQ_WS, FS)

    processed = processed.dropna()
    if len(processed) == 0:
        raise ValueError("Not enough data after feature engineering.")

    processed = processed.iloc[::2]

    kmeans = KMeans(n_clusters=5, n_init=20, random_state=0)
    processed["cluster"] = kmeans.fit_predict(processed[["acc_x", "acc_y", "acc_z"]])

    return processed


def features_row_for_model(df: pd.DataFrame, feature_names) -> pd.DataFrame:
    """Return one row aligned to model.feature_names_in_, filling missing with 0."""
    present = [c for c in feature_names if c in df.columns]
    if len(df) > 1 and present:
        row = df[present].mean(numeric_only=True)
    elif len(df) >= 1:
        row = df.iloc[-1]
    else:
        raise ValueError("No rows to build features from.")

    out = {
        name: float(row[name]) if name in row.index and pd.notna(row[name]) else 0.0
        for name in feature_names
    }
    return pd.DataFrame([out])
