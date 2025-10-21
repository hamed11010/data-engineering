# dashboard_app.py
# Real-time dashboard for Multi-City IoT Weather Data (Milestone 1 – Bonus)

import streamlit as st
import pandas as pd
import time
import os
import matplotlib.pyplot as plt

CSV_FILE = "sample_logs/readings.csv"

st.set_page_config(page_title="Real-Time Weather Dashboard", layout="centered")

st.title("🌦️ Real-Time Weather Dashboard – Multi-City")
st.caption("Displays live temperature & humidity from OpenWeatherMap API")

# Make sure file exists
if not os.path.exists(CSV_FILE):
    st.warning("No data yet. Run simulator_real_api.py to start generating readings.")
    st.stop()

# Load full data to detect available cities
full_df = pd.read_csv(CSV_FILE)
available_cities = sorted(full_df["city"].unique())
selected_city = st.selectbox("Select City", available_cities)

# Live refresh loop
placeholder = st.empty()

while True:
    df = pd.read_csv(CSV_FILE)
    # Filter by selected city
    df_city = df[df["city"] == selected_city]

    if df_city.empty:
        st.warning(f"No data yet for {selected_city}.")
        time.sleep(5)
        continue

    # Keep only the most recent 50 records
    df_city = df_city.tail(50)

    # Create charts
    fig, ax = plt.subplots(2, 1, figsize=(8, 6))
    ax[0].plot(df_city["timestamp"], df_city["temperature_c"], color="orange", marker="o")
    ax[0].set_title(f"Temperature (°C) – {selected_city}")
    ax[0].tick_params(axis="x", rotation=45)

    ax[1].plot(df_city["timestamp"], df_city["humidity"], color="blue", marker="o")
    ax[1].set_title(f"Humidity (%) – {selected_city}")
    ax[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()

    with placeholder.container():
        st.subheader(f"Last Reading → {df_city.iloc[-1]['temperature_c']}°C, "
                     f"{df_city.iloc[-1]['humidity']}% humidity, {df_city.iloc[-1]['weather']}")
        st.pyplot(fig)

    time.sleep(5)  # refresh every 5 seconds
