# daily_email_summary.py
# Send a daily friendly weather summary by email to all subscribed users

import os
import pandas as pd
from datetime import datetime
from mailer import send_email

CSV_FILE = "sample_logs/readings.csv"
SUBSCRIBERS_FILE = "subscribers.csv"


def build_advice(temp: float, humidity: float, weather: str, wind: float) -> list[str]:
    advice = []
    if temp < 19:
        advice.append("❄️ It's chilly—consider wearing something warm!")
    elif temp > 23:
        advice.append("🔥 Feels warm—dress light!")
    if humidity < 45:
        advice.append("💧 Air is dry—drink plenty of water!")
    elif humidity > 80:
        advice.append("🌫️ It's muggy—stay comfortable!")
    if "rain" in weather.lower():
        advice.append("☔️ Rain expected—take an umbrella!")
    if wind > 10:
        advice.append("🍃 Strong winds—take care if you're heading outside!")
    return advice


def main():
    if not os.path.exists(CSV_FILE):
        print("No CSV data file found, cannot send summary.")
        return

    if not os.path.exists(SUBSCRIBERS_FILE):
        print("No subscribers file found, nobody to email.")
        return

    # Load subscribers
    subscribers = []
    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            email = line.strip()
            if email:
                subscribers.append(email)

    if not subscribers:
        print("Subscribers list is empty, no emails will be sent.")
        return

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        print("CSV file is empty, nothing to summarize.")
        return

    # Convert timestamp to datetime for morning/evening logic
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    lines = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    for city in sorted(df["city"].unique()):
        city_df = df[df["city"] == city].copy()

        # Current reading (latest)
        latest = city_df.iloc[-1]
        temp_now = float(latest["temperature_c"])
        hum_now = float(latest["humidity"])
        wind_now = float(latest.get("wind_speed", 0))
        weather_now = str(latest.get("weather", ""))

        # Morning = earliest record after 06:00
        morning_df = city_df[city_df["timestamp"].dt.hour >= 6]
        morning = morning_df.iloc[0] if not morning_df.empty else latest

        # Evening = earliest record after 18:00
        evening_df = city_df[city_df["timestamp"].dt.hour >= 18]
        evening = evening_df.iloc[0] if not evening_df.empty else latest

        temp_morning = float(morning["temperature_c"])
        hum_morning = float(morning["humidity"])
        wind_morning = float(morning.get("wind_speed", 0))
        weather_morning = str(morning.get("weather", ""))

        temp_evening = float(evening["temperature_c"])
        hum_evening = float(evening["humidity"])
        wind_evening = float(evening.get("wind_speed", 0))
        weather_evening = str(evening.get("weather", ""))

        advice_now = build_advice(temp_now, hum_now, weather_now, wind_now)
        advice_morning = build_advice(temp_morning, hum_morning, weather_morning, wind_morning)
        advice_evening = build_advice(temp_evening, hum_evening, weather_evening, wind_evening)

        lines.append(f"City: {city}")
        lines.append(f"  Morning: {temp_morning:.1f}°C, {hum_morning:.0f}% humidity, {weather_morning}")
        for a in advice_morning:
            lines.append(f"    - {a}")
        lines.append(f"  Evening: {temp_evening:.1f}°C, {hum_evening:.0f}% humidity, {weather_evening}")
        for a in advice_evening:
            lines.append(f"    - {a}")
        lines.append(f"  Now: {temp_now:.1f}°C, {hum_now:.0f}% humidity, {weather_now}")
        for a in advice_now:
            lines.append(f"    - {a}")
        lines.append("")

    body = f"Daily weather summary ({now_str})\n\n" + "\n".join(lines)
    subject = "Your daily friendly weather summary"

    for email in subscribers:
        send_email(email, subject, body)
        print(f"Daily weather summary email sent to {email}.")


if __name__ == "__main__":
    main()
