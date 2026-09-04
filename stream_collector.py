import sys
import re
import csv
import os
from datetime import datetime

CSV_FILE = "telemetry.csv"

# ORA REALA de start a trecerii satelitului (schimb-o cu ora reala de pe pagina SatNOGS)
PASS_START_TIME = datetime.fromisoformat("2026-09-04T05:59:54")
script_start = datetime.now()

def current_real_time():
    elapsed = datetime.now() - script_start
    return (PASS_START_TIME + elapsed).isoformat()

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

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp"] + list(patterns.keys()))

current_record = {}
in_whole_orbit = False

def save_record(record):
    if len(record) > 1:
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp"] + list(patterns.keys()))
            writer.writerow(record)
        print(f"Salvata telemetrie la {record['timestamp']}")

for line in sys.stdin:
    line = line.strip()

    if "Realtime telemetry:" in line:
        current_record = {"timestamp": current_real_time()}
        in_whole_orbit = False
        continue

    if "Whole orbit" in line or "High resolution" in line or "Fitter message" in line:
        save_record(current_record)
        current_record = {}
        in_whole_orbit = True
        continue

    if in_whole_orbit and re.match(r'^Container:\s*$', line):
        save_record(current_record)
        current_record = {"timestamp": current_real_time()}
        continue

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

    if line.startswith("-> Packet from"):
        save_record(current_record)
        current_record = {}
        in_whole_orbit = False

save_record(current_record)