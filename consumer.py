import paho.mqtt.client as mqtt
import json
import time

# --- Configuration ---
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883
TOPIC = "weather/readings"  # Must MATCH producer's topic

def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe(TOPIC)
    print(f"Connected to MQTT Broker and subscribed to {TOPIC}!")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode()) 
        print(f"DEBUG: Received data: {payload}")

        temp = payload.get("temperature_c")
        humidity = payload.get("humidity")
        city = payload.get("city", "UnknownCity") 

        if temp is not None and float(temp) < 19.0:
            print(f"❄️ LOW TEMP ALERT! City: {city}, Temperature: {temp}°C (Bundle up, it's chilly!)")
        if temp is not None and float(temp) > 23.0:
            print(f"🔥 MODERATE HIGH TEMP ALERT! City: {city}, Temperature: {temp}°C (Feels warm!)")
        if humidity is not None and float(humidity) < 45.0:
            print(f"💧 LOW HUMIDITY ALERT! City: {city}, Humidity: {humidity}% (Stay hydrated!)")
        if humidity is not None and float(humidity) > 80.0:
            print(f"🌫️ HIGH HUMIDITY ALERT! City: {city}, Humidity: {humidity}% (It feels muggy!)")
    except Exception as e:
        print(f"Error processing message: {e}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

if __name__ == "__main__":
    try:
        print(f"Connecting to {BROKER_HOST}:{BROKER_PORT}, subscribing to '{TOPIC}' ...")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        print("\n🛑Stopped by user.")
