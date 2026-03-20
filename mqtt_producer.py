import paho.mqtt.client as mqtt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import csv
import time

# --- Configuration ---
CSV_FILE_TO_WATCH = "sample_logs/readings.csv"
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "weather/readings"

# --- Global variable to hold the CSV header ---
csv_header = []

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("CSV Watcher Producer connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

# --- Setup MQTT Client ---
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.loop_start() # Handles network in background

# --- Watchdog Handler ---
class MyFileHandler(FileSystemEventHandler):
    last_line = ""

    def on_modified(self, event):
        if event.src_path.endswith("readings.csv"):
            global csv_header
            try:
                with open(CSV_FILE_TO_WATCH, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if not lines:
                        return

                    if not csv_header:
                        csv_header = lines[0].strip().split(',')
                    new_line = lines[-1].strip()
                    if new_line != self.last_line and new_line:
                        self.last_line = new_line
                        csv_reader = csv.reader([new_line])
                        values = next(csv_reader)
                        if len(values) == len(csv_header):
                            json_payload = dict(zip(csv_header, values))
                            message = json.dumps(json_payload)
                            client.publish(MQTT_TOPIC, message)
                            print(f"Published new reading from CSV: {json_payload.get('city')}")
            except Exception as e:
                print(f"Error reading file: {e}")

if __name__ == "__main__":
    print(f"Watching file: {CSV_FILE_TO_WATCH}")
    print(f"Publishing new lines to MQTT topic: {MQTT_TOPIC}")
    event_handler = MyFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='sample_logs/', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        client.loop_stop()
        print("\n🛑 Watcher stopped by user.")
    observer.join()
