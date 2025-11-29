# dashboard_app.py
# Enhanced Real-Time Weather Dashboard with Innovations

import streamlit as st
import pandas as pd
import time
import os
import csv
import sys
from dotenv import load_dotenv

# Add project root to Python path so we can import mailer.py
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from mailer import send_email
from prediction_utils import predict_tomorrow_for_city


# Load environment variables from .env at project root (if needed later)
load_dotenv()

CSV_FILE = "sample_logs/readings.csv"

st.set_page_config(page_title="Real-Time Weather Dashboard", layout="centered")
st.title("🌦️ Real-Time Weather Dashboard – Multi-City")
st.caption("Displays live temperature & humidity from OpenWeatherMap API")

# ---- Email subscription (stored locally in subscribers.csv) ----
email_file = "subscribers.csv"

st.sidebar.subheader("Email Alerts")
email = st.sidebar.text_input("Enter Email for Daily & Severe Weather Alerts")
subscribe = st.sidebar.button("Subscribe")

if subscribe and email:
    try:
        # Load existing subscribers
        existing = set()
        if os.path.exists(email_file):
            with open(email_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        existing.add(row[0].strip())

        if email not in existing:
            # Save new subscriber
            with open(email_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([email])
            st.sidebar.success("You are subscribed to daily weather summaries!")

            # Send immediate welcome email with current city weather
            try:
                df_demo = pd.read_csv(CSV_FILE)
                df_city_demo = df_demo[df_demo["city"] == st.session_state.get("selected_city", "")]

                # If session_state has no city yet, fall back to all data
                if df_city_demo.empty:
                    df_city_demo = df_demo

                if not df_city_demo.empty:
                    latest_demo = df_city_demo.iloc[-1]
                    city_name = latest_demo.get("city", "your city")
                    temp = float(latest_demo["temperature_c"])
                    hum = float(latest_demo["humidity"])
                    weather = str(latest_demo.get("weather", ""))
                    wind = float(latest_demo.get("wind_speed", 0))

                    message_lines = [
                        "Hello 👋",
                        "",
                        f"Thanks for subscribing to weather updates.",
                        f"Current conditions in {city_name}:",
                        f"- Temperature: {temp:.1f}°C",
                        f"- Humidity: {hum:.0f}%",
                        f"- Weather: {weather}",
                    ]

                    if temp < 19:
                        message_lines.append("❄️ It's a bit chilly—consider wearing something warm!")
                    elif temp > 23:
                        message_lines.append("🔥 Feels warm—dress light!")
                    if "rain" in weather.lower():
                        message_lines.append("☔️ Rain is expected—an umbrella might help!")
                    if wind > 10:
                        message_lines.append("🍃 Quite windy—take care if you're heading outside!")

                    message_lines.append("")
                    message_lines.append("You will also receive a daily summary automatically. 👑")

                    body = "\n".join(message_lines)
                    send_email(
                        email,
                        f"Welcome to {city_name} weather updates",
                        body,
                    )
                else:
                    send_email(
                        email,
                        "Welcome to weather updates",
                        "Hello 👑, you are now subscribed to daily weather summaries.",
                    )
            except Exception as mail_err:
                st.sidebar.warning(f"Subscribed, but could not send welcome email: {mail_err}")
        else:
            st.sidebar.info("This email is already subscribed.")
    except Exception as e:
        st.sidebar.error(f"Could not save email: {e}")

# ---- Data File Existence Check ----
if not os.path.exists(CSV_FILE):
    st.warning("No data yet. Run simulator_real_api.py to start generating readings.")
    st.stop()

# ---- Load and Prepare Data ----
full_df = pd.read_csv(CSV_FILE)
available_cities = sorted(full_df["city"].unique())

# ---- City Selector (Single City) ----
selected_city = st.selectbox("Select City", available_cities)
st.session_state["selected_city"] = selected_city

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
    temp = float(latest["temperature_c"])
    humidity = float(latest["humidity"])
    wind = float(latest.get("wind_speed", 0))
    weather = latest.get("weather", "").lower()

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
    avg_temp = df_city["temperature_c"].astype(float).mean()
    avg_hum = df_city["humidity"].astype(float).mean()
    st.write("#### Historical Averages (last 50 readings)")
    st.write(f"**Average Temperature:** {avg_temp:.2f}°C")
    st.write(f"**Average Humidity:** {avg_hum:.2f}%")
    
        # ---- Simple AI Prediction for Tomorrow ----
    try:
        pred_temp, pred_hum = predict_tomorrow_for_city(df, selected_city)
        if pred_temp is not None and pred_hum is not None:
            st.write("#### Predicted for tomorrow (simple trend)")
            st.write(f"**Predicted Temperature:** {pred_temp:.2f}°C")
            st.write(f"**Predicted Humidity:** {pred_hum:.2f}%")
        else:
            st.write("#### Predicted for tomorrow (simple trend)")
            st.write("Not enough data yet to predict reliably.")
    except Exception as e:
        st.write("#### Predicted for tomorrow (simple trend)")
        st.write(f"Could not compute prediction: {e}")


    # ---- Multi-City Comparison Section ----
    st.header("Compare Cities Side by Side")
    city_options = st.multiselect(
        "Select up to 2 cities for comparison",
        available_cities,
        default=available_cities[:2],
        key="city_compare_multiselect", 
    )
    
    if len(city_options) == 2:
        comp_df = df[df["city"].isin(city_options)].copy()
        comp_df["temperature_c"] = comp_df["temperature_c"].astype(float)
        comp_df["humidity"] = comp_df["humidity"].astype(float)
        display_df = pd.concat(
            [
                comp_df[comp_df["city"] == city_options[0]].tail(30),
                comp_df[comp_df["city"] == city_options[1]].tail(30),
            ]
        )
        st.write("#### Temperature Comparison (last 30 readings)")
        st.line_chart(display_df.pivot(index="timestamp", columns="city", values="temperature_c"))
        st.write("#### Humidity Comparison (last 30 readings)")
        st.line_chart(display_df.pivot(index="timestamp", columns="city", values="humidity"))

    time.sleep(5)
