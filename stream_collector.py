import sys
import re
import csv
import os
from datetime import datetime

CSV_FILE = "telemetry.csv"

# Regex-uri pentru parametrii principali
patterns = {
    "battery_voltage_mV": re.compile(r"batteryvoltage\s*=\s*(\d+)"),
    "system_current_mA": re.compile(r"systemcurrent\s*=\s*(\d+)"),
    "battery_temp_C": re.compile(r"batterytemp\s*=\s*(-?\d+)"),
    "paneltemp_xp": re.compile(r"paneltempX\+\s*=\s*([-\d\.]+)"),
    "paneltemp_xn": re.compile(r"paneltempX-\s*=\s*([-\d\.]+)"),
    "paneltemp_yp": re.compile(r"paneltempY\+\s*=\s*([-\d\.]+)"),
    "paneltemp_yn": re.compile(r"paneltempY-\s*=\s*([-\d\.]+)"),
    "bus_3v3_voltage_mV": re.compile(r"3v3voltage\s*=\s*(\d+)"),
    "bus_3v3_current_mA": re.compile(r"3v3current\s*=\s*(\d+)"),
    "rx_rssi": re.compile(r"rxrssi\s*=\s*(\d+)"),
    "rx_doppler": re.compile(r"rxdoppler\s*=\s*(\d+)"),
    "in_eclipse": re.compile(r"eclipse\s*=\s*(True|False)"),
    "in_safe_mode": re.compile(r"safemode\s*=\s*(True|False)")
}

# Inițializare fișier CSV dacă nu există
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp"] + list(patterns.keys()))

current_record = {}

# Procesare stream linie cu linie
for line in sys.stdin:
    line = line.strip()
    
    # Detecție pachet nou
    if "Realtime telemetry:" in line:
        current_record = {"timestamp": datetime.now().isoformat()}

    for key, pattern in patterns.items():
        m = pattern.search(line)
        if m:
            val = m.group(1)
            if val in ["True", "False"]:
                current_record[key] = (val == "True")
            elif "." in val:
                current_record[key] = float(val)
            else:
                current_record[key] = int(val)

    # La finalul blocului RTT (sau la întâlnirea liniei de Whole Orbit), salvăm rândul
    if ("Whole orbit" in line or "High resolution" in line or "Fitter message" in line) and "timestamp" in current_record:
        if len(current_record) > 1:
            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp"] + list(patterns.keys()))
                writer.writerow(current_record)
            print(f"Salvată telemetrie la {current_record['timestamp']}")
        current_record = {}