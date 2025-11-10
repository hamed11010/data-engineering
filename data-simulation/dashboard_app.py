# dashboard_app.py
# Enhanced Real-Time Weather Dashboard with Innovations

import streamlit as st
import pandas as pd
import time
import os

CSV_FILE = "sample_logs/readings.csv"

st.set_page_config(page_title="Real-Time Weather Dashboard", layout="centered")
st.title("🌦️ Real-Time Weather Dashboard – Multi-City")
st.caption("Displays live temperature & humidity from OpenWeatherMap API")

# ---- Demo Email Alert Input (feature showcase) ----
email = st.sidebar.text_input("Enter Email for Severe Weather Alerts (Demo Only)")
if email:
    st.sidebar.success("Subscription active! You would receive email alerts for severe weather (demo feature).")

# ---- Data File Existence Check ----
if not os.path.exists(CSV_FILE):
    st.warning("No data yet. Run simulator_real_api.py to start generating readings.")
    st.stop()

# ---- Load and Prepare Data ----
full_df = pd.read_csv(CSV_FILE)
available_cities = sorted(full_df["city"].unique())

# ---- City Selector (Single City) ----
selected_city = st.selectbox("Select City", available_cities)

# ---- Real-Time Dashboard Loop ----
placeholder = st.empty()

while True:
    df = pd.read_csv(CSV_FILE)
    df_city = df[df["city"] == selected_city]
    if df_city.empty:
        st.warning(f"No data yet for {selected_city}.")
        time.sleep(5)
        continue

    # Only last 50 readings for clarity
    df_city = df_city.tail(50)
    latest = df_city.iloc[-1]
    temp = float(latest['temperature_c'])
    humidity = float(latest['humidity'])
    wind = float(latest.get('wind_speed', 0))
    weather = latest.get('weather', '').lower()

    # ---- Weather Advice/Alert Panel ----
    advice = []
    if temp < 19:
        advice.append("❄️ It's chilly—consider wearing something warm!")
    elif temp > 23:
        advice.append("🔥 Feels warm—dress light!")
    if humidity < 45:
        advice.append("💧 Air is dry—drink plenty of water!")
    elif humidity > 80:
        advice.append("🌫️ It's muggy—stay comfortable!")
    if "rain" in weather:
        advice.append("☔️ Rain expected—take an umbrella!")
    if wind > 10:
        advice.append("🍃 Strong winds—take care if outside!")

    # ---- Improved Single City Chart ----
    st.subheader(f"Last Reading → {temp:.2f}°C, {humidity:.2f}% humidity, {latest['weather']}")
    if advice:
        st.markdown(f"**Weather Advice for {selected_city}:**")
        for a in advice:
            st.info(a)

    st.write("#### Temperature & Humidity (last 50 readings)")
    st.line_chart(df_city.set_index("timestamp")[["temperature_c", "humidity"]])

    # ---- Historical Averages ----
    avg_temp = df_city['temperature_c'].astype(float).mean()
    avg_hum = df_city['humidity'].astype(float).mean()
    st.write("#### Historical Averages (last 50 readings)")
    st.write(f"**Average Temperature:** {avg_temp:.2f}°C")
    st.write(f"**Average Humidity:** {avg_hum:.2f}%")

    # ---- Multi-City Comparison Section ----
    st.header("Compare Cities Side by Side")
    city_options = st.multiselect("Select up to 2 cities for comparison", available_cities, default=available_cities[:2])
    if len(city_options) == 2:
        comp_df = df[df['city'].isin(city_options)].copy()
        comp_df['temperature_c'] = comp_df['temperature_c'].astype(float)
        comp_df['humidity'] = comp_df['humidity'].astype(float)
        display_df = pd.concat([
            comp_df[comp_df['city'] == city_options[0]].tail(30),
            comp_df[comp_df['city'] == city_options[1]].tail(30)
        ])
        st.write("#### Temperature Comparison (last 30 readings)")
        st.line_chart(display_df.pivot(index="timestamp", columns="city", values="temperature_c"))
        st.write("#### Humidity Comparison (last 30 readings)")
        st.line_chart(display_df.pivot(index="timestamp", columns="city", values="humidity"))

    time.sleep(5)
