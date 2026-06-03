import joblib
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.DataTransformation import LowPassFilter
from features.inference_features import engineer_features_from_raw, features_row_for_model
from .input_validation import (
    RAW_SENSOR_COLUMNS,
    clean_sensor_dataframe,
    friendly_validation_error,
)

MIN_CONFIDENCE_HINT = 0.35


class ExercisePredictionPipeline:
    """Production-ready ML prediction pipeline for exercise detection"""
    
    def __init__(self, model_path=None):
        """
        Initialize pipeline with trained model
        
        Args:
            model_path: Path to saved model. If None, uses default location
        """
        if model_path is None:
            # Use absolute path to models directory
            model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
            model_path = os.path.abspath(os.path.join(model_dir, "trained_model.pkl"))
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please train and save the model first.")
        
        self.model = joblib.load(model_path)
        self.feature_names = list(self.model.feature_names_in_)
        self.low_pass = LowPassFilter()
        self.fs = 1000 / 200  # Sampling frequency
    
    def compute_rep_count(self, df, column="acc_r", cutoff=0.4):
        """
        Count repetitions using peak detection
        
        Args:
            df: DataFrame with sensor data
            column: Column to analyze (acc_r, gyro_x, etc.)
            cutoff: Cutoff frequency for low-pass filter
            
        Returns:
            Number of repetitions detected
        """
        from scipy.signal import argrelextrema
        
        # Add lowpass filter column if not exists
        if f"{column}_lowpass" not in df.columns:
            df = self.low_pass.low_pass_filter(
                df.copy(),
                col=column,
                sampling_frequency=self.fs,
                cutoff_frequency=cutoff,
                order=10
            )
        
        # Find peaks
        indexes = argrelextrema(df[f"{column}_lowpass"].values, np.greater)
        num_peaks = len(indexes[0])
        
        return num_peaks
    
    def preprocess_sensor_data(self, sensor_dict):
        """
        Convert raw sensor readings to processed format
        
        Args:
            sensor_dict: Dict with columns like 'acc_x', 'acc_y', etc.
            
        Returns:
            DataFrame with computed features
        """
        df = pd.DataFrame(sensor_dict)
        
        # Compute derived features
        df['acc_r'] = np.sqrt(df['acc_x']**2 + df['acc_y']**2 + df['acc_z']**2)
        df['gyro_r'] = np.sqrt(df['gyro_x']**2 + df['gyro_y']**2 + df['gyro_z']**2)
        
        return df

    def _prepare_model_input(self, df: pd.DataFrame) -> pd.DataFrame:
        """Raw sensor -> engineered features; pre-engineered CSV -> aligned single row."""
        has_raw_only = set(RAW_SENSOR_COLUMNS).issubset(df.columns) and not set(
            self.feature_names
        ).issubset(df.columns)

        if has_raw_only:
            engineered = engineer_features_from_raw(df)
            return features_row_for_model(engineered, self.feature_names)

        missing = [c for c in self.feature_names if c not in df.columns]
        if missing:
            raise ValueError(
                f"CSV is missing {len(missing)} features the model needs "
                f"(e.g. {missing[:3]}…). Upload raw sensor CSV "
                f"(columns: {', '.join(RAW_SENSOR_COLUMNS)}) or a full feature file."
            )

        return features_row_for_model(df, self.feature_names)
    
    def predict(self, sensor_data, return_reps=True):
        """
        Make prediction on sensor data
        
        Args:
            sensor_data: Dict or DataFrame with accelerometer & gyroscope readings
            return_reps: Whether to also estimate rep count
            
        Returns:
            Dict with prediction results
        """
        try:
            notices = []
            if isinstance(sensor_data, dict):
                df = pd.DataFrame(sensor_data)
            else:
                df = sensor_data.copy()

            has_all_features = set(self.feature_names).issubset(df.columns)
            has_raw = set(RAW_SENSOR_COLUMNS).issubset(df.columns)

            if not has_raw and not has_all_features:
                partial = [c for c in RAW_SENSOR_COLUMNS if c in df.columns]
                if partial:
                    raise ValueError("partial_sensors")
                raise ValueError("not_sensor_data")

            if has_raw and not has_all_features:
                df, notices = clean_sensor_dataframe(df)

            df_for_reps = df
            if set(RAW_SENSOR_COLUMNS).issubset(df.columns):
                df_for_reps = self.preprocess_sensor_data(df.to_dict(orient="list"))

            df_pred = self._prepare_model_input(df)

            exercise = self.model.predict(df_pred)[0]
            
            probabilities = self.model.predict_proba(df_pred)[0]
            confidence = float(np.max(probabilities))
            
            # Estimate reps if requested (use raw data if available)
            reps = None
            if return_reps and 'acc_r' in df_for_reps.columns:
                cutoff_map = {
                    'bench': 0.4,
                    'squat': 0.35,
                    'row': 0.65,
                    'ohp': 0.35,
                    'dead': 0.4
                }
                column_map = {
                    'bench': 'acc_r',
                    'squat': 'acc_r',
                    'row': 'gyro_x' if 'gyro_x' in df_for_reps.columns else 'acc_r',
                    'ohp': 'acc_r',
                    'dead': 'acc_r'
                }
                cutoff = cutoff_map.get(exercise, 0.4)
                column = column_map.get(exercise, 'acc_r')
                if column in df_for_reps.columns:
                    reps = self.compute_rep_count(df_for_reps, column=column, cutoff=cutoff)
            
            result = {
                'success': True,
                'exercise': exercise,
                'confidence': confidence,
                'confidence_percent': round(confidence * 100, 2),
                'reps': reps,
                'all_probabilities': {
                    cls: float(p) for cls, p in zip(self.model.classes_, probabilities)
                },
                'notices': notices,
            }
            if confidence < MIN_CONFIDENCE_HINT:
                result['notices'] = notices + [
                    "The guess is uncertain — try a longer, steadier recording for a clearer result."
                ]
            return result
        
        except Exception as e:
            err = str(e)
            if err in ("partial_sensors", "not_sensor_data"):
                msg = friendly_validation_error(err)
            elif err.startswith("missing_sensors:") or err.startswith("too_short:") or err == "too_many_gaps":
                msg = friendly_validation_error(err)
            elif "Need at least" in err and "got" in err:
                import re
                m = re.search(r"got (\d+)", err)
                msg = friendly_validation_error(f"too_short:{m.group(1) if m else '0'}")
            elif "CSV is missing" in err or "feature" in err.lower():
                msg = friendly_validation_error("not_sensor_data")
            elif "monotonic_cst" in err:
                msg = "The app needs a quick update on the server. Please try again later or use Try demo."
            else:
                mapped = friendly_validation_error(err)
                msg = mapped if mapped != err else "Something went wrong. Try a different file or use Try demo."
            return {'success': False, 'error': msg}
    
    def predict_batch(self, sensor_data_list):
        """
        Make predictions on multiple data samples
        
        Args:
            sensor_data_list: List of sensor data dicts
            
        Returns:
            List of predictions
        """
        results = []
        for data in sensor_data_list:
            results.append(self.predict(data))
        return results


# Global pipeline instance
_pipeline_instance = None

def get_pipeline(force_reload=False):
    """Get or create pipeline instance"""
    global _pipeline_instance
    if force_reload:
        _pipeline_instance = None
    if _pipeline_instance is None:
        _pipeline_instance = ExercisePredictionPipeline()
    return _pipeline_instance
