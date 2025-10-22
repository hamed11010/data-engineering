import paho.mqtt.client as mqtt
import json
import time

# --- Configuration ---
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "weather/readings" # Must MATCH producer's topic

# --- Event 1: The "On Connect" Callback ---
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)
    print(f"Connected to MQTT Broker and subscribed to {TOPIC}!")

# --- Event 2: The "On Message" Callback ---
def on_message(client, userdata, msg):
    
    try:
        payload = json.loads(msg.payload.decode()) 
        
        print(f"DEBUG: Received data: {payload}")

        # --- THIS IS YOUR ALERT LOGIC ---
        temp = payload.get("temperature_c")
        humidity = payload.get("humidity")
        city = payload.get("city", "UnknownCity") 

        if temp is not None and float(temp) > 35.0:
            print(f"🚨 HIGH TEMP ALERT! 🚨 City: {city}, Temperature: {temp}°C")

        if humidity is not None and float(humidity) < 20.0:
            print(f"💧 LOW HUMIDITY ALERT! 💧 City: {city}, Humidity: {humidity}%")
            
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