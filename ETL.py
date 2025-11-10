import pandas as pd
from sqlalchemy import create_engine

# STEP 1: Connect to PostgreSQL via Docker
engine = create_engine('postgresql://admin:admin@localhost:5432/iot_data')

# STEP 2: Extract data from your CSV file (reads 'readings.csv')
df = pd.read_csv('sample_logs/readings.csv')

# STEP 3: Transform data (add anomaly flags and friendly message columns)

# Moderate high temperature (> 23°C)
df['mod_high_temp'] = df['temperature_c'].astype(float) > 23
df['temp_message'] = df['temperature_c'].astype(float).apply(
    lambda x: "Feels warm—enjoy the sunshine! ☀️" if x > 23 else (
        "It's a bit chilly—consider wearing something warm! 😊" if x < 19 else ""
    )
)

# Low temperature (< 19°C)
df['low_temp'] = df['temperature_c'].astype(float) < 19

# Low humidity (< 45%)
df['low_humidity'] = df['humidity'].astype(float) < 45
df['humidity_message'] = df['humidity'].astype(float).apply(
    lambda x: "Air is dry—drink plenty of water! 💧" if x < 45 else (
        "It's very humid—feels muggy! 🌫️" if x > 80 else ""
    )
)

# High humidity (> 80%)
df['high_humidity'] = df['humidity'].astype(float) > 80

# Rain warning — gentle umbrella message
df['rain_warning'] = df['weather'].str.contains('rain', case=False)
df['umbrella_message'] = df['rain_warning'].apply(
    lambda x: "Rain is expected—an umbrella might come in handy! ☔️" if x else ""
)

# Wind warning — caring message
df['windy_warning'] = df['wind_speed'].astype(float) > 10
df['wind_message'] = df['windy_warning'].apply(
    lambda x: "Quite a windy day—take care if you're heading outside! 🍃" if x else ""
)

# STEP 4: Load transformed data into PostgreSQL as a new table 'weather_readings'
df.to_sql('weather_readings', engine, if_exists='replace', index=False)

print("✅ ETL complete! Data loaded into 'weather_readings' table.")
