import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# --- Configuration ---
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "weather/readings"  # Must MATCH producer's topic
ALERT_FILE = "alerts.txt"   

# --- Helper Function to Log Alerts ---
def log_alert(alert_message):
    """
    Prints an alert to the console and appends it, with a timestamp,
    to the alert log file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_log_entry = f"[{timestamp}] {alert_message}"
    
    # 1. Print to console (as before)
    print(full_log_entry)
    
    # 2. Append to file
    try:
        with open(ALERT_FILE, "a", encoding="utf-8") as f:
            f.write("="*100 + "\n")
            f.write(full_log_entry + "\n")
            f.write("="*100 + "\n")
    except Exception as e:
        print(f"CRITICAL: Failed to write alert to file {ALERT_FILE}: {e}")

# --- Event 1: The "On Connect" Callback ---
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)
    print(f"Connected to MQTT Broker and subscribed to {TOPIC}!")
    print(f"Alerts will be logged to: {ALERT_FILE}")  # <--- Added this line

# --- Event 2: The "On Message" Callback ---
def on_message(client, userdata, msg):
    
    try:
        payload = json.loads(msg.payload.decode()) 
        
        print(f"DEBUG: Received data: {payload}")

        temp = payload.get("temperature_c")
        humidity = payload.get("humidity")
        wind_speed = payload.get("wind_speed")
        pressure = payload.get("pressure")
        city = payload.get("city", "UnknownCity") 

        if temp is not None and float(temp) > 35.0:
            log_alert(f"🚨 HIGH TEMP ALERT! 🚨 City: {city}, Temperature: {temp}°C")

        if humidity is not None and float(humidity) < 20.0:
            log_alert(f"💧 LOW HUMIDITY ALERT! 💧 City: {city}, Humidity: {humidity}%")

        if wind_speed is not None and float(wind_speed) > 3.0:
            log_alert(f"🌪️ HIGH WIND SPEED ALERT! 🌪️ City: {city}, Wind Speed: {wind_speed} km/h")

        if pressure is not None and float(pressure) > 1000.0:
            log_alert(f"🌧️ HIGH PRESSURE ALERT! 🌧️ City: {city}, Pressure: {pressure} hPa")

    except Exception as e:
        print(f"Error processing message: {e}")

# --- Setup ---
# 1. Create a new client
client = mqtt.Client()

# 2. Attach functions (callbacks) to the client
client.on_connect = on_connect
client.on_message = on_message

if __name__ == "__main__":
    
    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        print("\n🛑Stopped by user.")