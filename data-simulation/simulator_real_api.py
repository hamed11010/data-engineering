# simulator_real_api.py
# Milestone 1 - Multi-City Version
# Fetches real-time weather data from OpenWeatherMap API for multiple cities every few seconds
# and saves it to a CSV file.

import requests
import time
import os
import csv
import itertools
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITIES = os.getenv("CITIES", "Cairo").split(",")  # now supports multiple cities
INTERVAL = int(os.getenv("INTERVAL_SECONDS", 5))
OUTPUT_CSV = "sample_logs/readings.csv"
MAX_READINGS = 10  # stop automatically after 10 cycles

if not API_KEY:
    raise SystemExit("Error: Please set your OPENWEATHER_API_KEY in the .env file.")

# Ensure the output folder exists
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)


def fetch_weather(city, api_key):
    """Fetches current weather data from OpenWeatherMap API."""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city.strip(), "appid": api_key, "units": "metric"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_weather(data):
    """Extracts only useful fields."""
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "city": data.get("name"),
        "temperature_c": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "weather": data["weather"][0]["description"]
    }



def write_csv(row):
    """Appends a new weather record to the CSV file."""
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def main():
    print(f"Starting multi-city weather data ingestion for {', '.join(CITIES)} every {INTERVAL} seconds...\n")

    try:
        for i in itertools.count(1):
            if i > MAX_READINGS:
                print(f"\n✅ Data generation finished after {MAX_READINGS} cycles.")
                break

            for city in CITIES:
                try:
                    raw_data = fetch_weather(city, API_KEY)
                    weather_row = parse_weather(raw_data)
                    write_csv(weather_row)
                    print(
                        f"Reading {i}/{MAX_READINGS} → "
                        f"[{weather_row['timestamp']}] {weather_row['city']}: "
                        f"{weather_row['temperature_c']}°C, "
                        f"{weather_row['humidity']}% humidity, {weather_row['weather']}"
                    )
                except Exception as e:
                    print(f"⚠️ Error fetching data for {city}: {e}")

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Data generation stopped by user.")


if __name__ == "__main__":
    main()
