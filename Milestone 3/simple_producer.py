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

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("CSV Watcher Producer connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

# --- Setup MQTT Client ---
client = mqtt.Client()
client.on_connect = on_connect
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.loop_start() # Handles network in the background

# --- This is the class that watches the file ---
class MyFileHandler(FileSystemEventHandler):
    
    # We need to keep track of the last line we read
    last_line = ""

    def on_modified(self, event):
        # This event fires on any change, so we check if it's our file
        if event.src_path.endswith("readings.csv"):
            global csv_header
            try:
                with open(CSV_FILE_TO_WATCH, 'r', encoding='utf-8') as f:
                    # Read all lines
                    lines = f.readlines()
                    if not lines:
                        return

                    # Get the header if we don't have it
                    if not csv_header:
                        csv_header = lines[0].strip().split(',')
                    
                    # Get the very last line
                    new_line = lines[-1].strip()

                    # Check if this is truly a new line, not just a re-save
                    if new_line != self.last_line and new_line:
                        self.last_line = new_line
                        
                        # --- Convert CSV line to JSON ---
                        # Use csv.reader to handle commas inside quotes
                        csv_reader = csv.reader([new_line])
                        values = next(csv_reader)
                        
                        if len(values) == len(csv_header):
                            # Zip header and values together into a dictionary
                            json_payload = dict(zip(csv_header, values))
                            
                            # Convert dictionary to JSON string for sending
                            message = json.dumps(json_payload)
                            
                            # --- Publish to MQTT ---
                            client.publish(MQTT_TOPIC, message)
                            print(f"Published new reading from CSV: {json_payload.get('city')}")
                        
            except Exception as e:
                # Handle race conditions (file being written while we read)
                print(f"Error reading file: {e}")

# --- Main setup for the file watcher ---
if __name__ == "__main__":
    print(f"Watching file: {CSV_FILE_TO_WATCH}")
    print(f"Publishing new lines to MQTT topic: {MQTT_TOPIC}")
    
    # Set up the file observer
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