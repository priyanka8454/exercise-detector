"""Clean and validate user-uploaded sensor data before prediction."""

import re
from typing import List, Tuple

import numpy as np
import pandas as pd

RAW_SENSOR_COLUMNS = ["acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"]
MIN_ROWS = 16

# Common alternate column names from export tools
COLUMN_ALIASES = {
    "accelerometer_x": "acc_x",
    "accelerometer_y": "acc_y",
    "accelerometer_z": "acc_z",
    "accel_x": "acc_x",
    "accel_y": "acc_y",
    "accel_z": "acc_z",
    "gyroscope_x": "gyro_x",
    "gyroscope_y": "gyro_y",
    "gyroscope_z": "gyro_z",
    "x": "acc_x",
    "y": "acc_y",
    "z": "acc_z",
}


def _normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", str(name).strip().lower())


def clean_sensor_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Prepare raw sensor data: fix names, drop empty rows, fill small gaps.
    Returns cleaned dataframe and user-facing notices (not errors).
    """
    notices: List[str] = []
    work = df.copy()

    # Normalize headers and apply aliases
    rename_map = {}
    for col in work.columns:
        key = _normalize_name(col)
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
        elif key in RAW_SENSOR_COLUMNS:
            rename_map[col] = key
    if rename_map:
        work = work.rename(columns=rename_map)
        notices.append("We matched your column names to the sensor format.")

    present = [c for c in RAW_SENSOR_COLUMNS if c in work.columns]
    missing = [c for c in RAW_SENSOR_COLUMNS if c not in work.columns]

    if missing:
        raise ValueError(
            "missing_sensors:" + ",".join(missing)
        )

    work = work[present].apply(pd.to_numeric, errors="coerce")
    rows_before = len(work)
    work = work.dropna(how="all")
    if len(work) < rows_before:
        notices.append(f"We removed {rows_before - len(work)} empty rows.")

    if len(work) < MIN_ROWS:
        raise ValueError(
            f"too_short:{len(work)}"
        )

    # Fill gaps inside each sensor column (missing cells / short dropouts)
    filled = 0
    for col in RAW_SENSOR_COLUMNS:
        na_count = int(work[col].isna().sum())
        if na_count:
            work[col] = work[col].interpolate(limit_direction="both").bfill().ffill()
            filled += na_count
    if filled:
        notices.append(f"We filled in {filled} missing numbers so the analysis could run.")

    if work[RAW_SENSOR_COLUMNS].isna().any().any():
        raise ValueError("too_many_gaps")

    return work, notices


def friendly_validation_error(message: str) -> str:
    """Turn internal validation codes into simple messages."""
    if message.startswith("missing_sensors:"):
        parts = message.split(":", 1)[-1].split(",")
        labels = {
            "acc_x": "side-to-side movement (acc_x)",
            "acc_y": "up-down movement (acc_y)",
            "acc_z": "forward-back movement (acc_z)",
            "gyro_x": "rotation X",
            "gyro_y": "rotation Y",
            "gyro_z": "rotation Z",
        }
        desc = ", ".join(labels.get(p, p) for p in parts if p)
        return (
            f"Your file is missing movement data we need ({desc}). "
            "Export all accelerometer and gyroscope axes from your sensor app."
        )
    if message.startswith("too_short:"):
        n = message.split(":")[-1]
        return (
            f"Your recording is too short ({n} rows). "
            "Record at least a few seconds of the exercise and try again."
        )
    if message == "too_many_gaps":
        return "Too many blank values in the file. Re-export the workout or use Try demo."
    if message == "partial_sensors":
        return "Your file only has some movement sensors. We need all 6 (accelerometer + gyroscope)."
    if message == "not_sensor_data":
        return "This file does not look like workout sensor data. Export from your fitness sensor app."
    return message
