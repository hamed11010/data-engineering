# prediction_utils.py
# Simple trend-based prediction for next-day temperature and humidity

import pandas as pd
import numpy as np


def predict_tomorrow_for_city(df: pd.DataFrame, city: str):
    """
    df: full dataframe with columns: timestamp, city, temperature_c, humidity
    city: city name to filter
    Returns (pred_temp, pred_hum) or (None, None) if not enough data.
    """
    city_df = df[df["city"] == city].copy()
    if city_df.shape[0] < 5:
        return None, None  # not enough data

    # Ensure correct types and sort by time
    city_df = city_df.sort_values("timestamp")
    city_df["temperature_c"] = city_df["temperature_c"].astype(float)
    city_df["humidity"] = city_df["humidity"].astype(float)

    # Use last N points
    N = min(50, city_df.shape[0])
    recent = city_df.tail(N).copy()
    recent = recent.reset_index(drop=True)
    recent["t"] = np.arange(len(recent))  # time index 0..N-1

    # Simple linear regression: temp = a*t + b, hum = c*t + d
    t = recent["t"].values
    temp_vals = recent["temperature_c"].values
    hum_vals = recent["humidity"].values

    # Fit line using polyfit
    a, b = np.polyfit(t, temp_vals, 1)
    c, d = np.polyfit(t, hum_vals, 1)

    # Predict next time step (t_next = N)
    t_next = len(recent)
    pred_temp = a * t_next + b
    pred_hum = c * t_next + d

    return float(pred_temp), float(pred_hum)
