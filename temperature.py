import random
import time
import json
import logging
from collections import deque
import statistics

# --- Configuration ---
WINDOW_SIZE = 10  # number of recent values to calculate moving average and std
TEMP_THRESHOLD = 75  # absolute temperature limit in °C
Z_SCORE_LIMIT = 2.5  # z-score above which anomaly is flagged

# Simulated machine list
MACHINES = ["Lathe_01", "Milling_02", "Drill_03"]

# Set up logging
logging.basicConfig(filename='temperature_alerts.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Sliding window per machine
machine_temp_data = {machine: deque(maxlen=WINDOW_SIZE) for machine in MACHINES}

# --- Core Functionality ---

def simulate_temperature(machine):
    """
    Simulate temperature data for a given machine.
    Normal: 50-65°C, Random spikes added to simulate issues.
    """
    base = random.uniform(50, 65)
    if random.random() < 0.1:  # 10% chance of anomaly
        return round(base + random.uniform(15, 30), 2)
    return round(base, 2)

def detect_anomaly(machine, temp):
    """
    Detects anomaly using z-score and threshold.
    """
    readings = machine_temp_data[machine]
    readings.append(temp)

    if len(readings) < 5:
        return False, None  # not enough data yet

    mean = statistics.mean(readings)
    stdev = statistics.stdev(readings)

    if stdev == 0:
        return False, None

    z_score = (temp - mean) / stdev

    if temp > TEMP_THRESHOLD or z_score > Z_SCORE_LIMIT:
        reason = "HIGH_TEMP" if temp > TEMP_THRESHOLD else "Z_SCORE_SPIKE"
        return True, {
            "machine_id": machine,
            "temperature": temp,
            "z_score": round(z_score, 2),
            "mean_temp": round(mean, 2),
            "anomaly_reason": reason,
            "timestamp": time.time()
        }

    return False, None

def generate_alert(anomaly_data):
    """
    Output alert as JSON.
    """
    alert = {
        "type": "TEMP_ANOMALY",
        "machine": anomaly_data["machine_id"],
        "temperature": anomaly_data["temperature"],
        "z_score": anomaly_data["z_score"],
        "reason": anomaly_data["anomaly_reason"],
        "timestamp": anomaly_data["timestamp"]
    }

    alert_json = json.dumps(alert)
    logging.info(f"ALERT: {alert_json}")
    print(alert_json)  # This can be piped to a message queue, dashboard, or KG

# --- Main Monitoring Loop ---

def run_monitoring(cycles=50, delay=1):
    """
    Run the monitoring simulation loop.
    """
    print("Starting temperature monitoring...\n")
    for _ in range(cycles):
        for machine in MACHINES:
            temp = simulate_temperature(machine)
            is_anomaly, data = detect_anomaly(machine, temp)
            if is_anomaly:
                generate_alert(data)
        time.sleep(delay)

if __name__ == "__main__":
    run_monitoring()
