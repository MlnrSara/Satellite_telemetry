import json
import re
import datetime
import math
import pandas as pd

def convert_panel_temp(raw_adc):
    """
    Convertește valoarea brută de 10 biți de la termistorii panourilor solare
    în grade Celsius folosind ecuația Steinhart-Hart.
    """
    # Protecție pentru a evita împărțirea la zero
    if raw_adc <= 0 or raw_adc >= 1023:
        return None 
        
    # 1. Calcularea rezistenței termistorului
    # Presupunem un ADC pe 10 biți (valori 0-1023) și un rezistor fix (divizor) de 10k Ohmi.
    R_DIVIDER = 10000.0 
    r_thermistor = R_DIVIDER * ((1023.0 / raw_adc) - 1.0)
    
    # 2. Coeficienții Steinhart-Hart (Valori tipice pentru un termistor NTC de 10k)
    # Notă: Pentru o precizie de 100% comparată cu senzorii fizici AMSAT, 
    # acești coeficienți hardware specifici ar trebui preluați din codul sursă al echipajului.
    A = 0.001129148
    B = 0.000234125
    C = 0.0000000876741
    
    # 3. Aplicarea formulei
    ln_r = math.log(r_thermistor)
    temp_k = 1.0 / (A + B * ln_r + C * (ln_r ** 3))
    
    # Conversia din Kelvin în grade Celsius
    temp_c = temp_k - 273.15
    
    return round(temp_c, 2)

def extract_bits(bit_string, start, length):
    """Extrage un număr specific de biți și îi convertește într-un număr întreg"""
    return int(bit_string[start:start+length], 2)
def to_signed_8bit(val):
    """Convertește un număr fără semn de 8 biți într-unul cu semn (complement de 2)"""
    return val - 256 if val > 127 else val

def parse_funcube_frames(file_path):
    telemetry_data = []
    current_frame_hex = ""
    
    # Offset-ul în octeți unde începe secțiunea RTT în cadrele tale (ajustează dacă e necesar)
    RTT_OFFSET = 1 
    base_time = datetime.datetime.now() 
    frame_count = 0

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            if re.match(r'^[0-9a-fA-F]{4}:', line):
                hex_chunk = line.split(':')[1].replace(' ', '').strip()
                current_frame_hex += hex_chunk
                
            elif "*****" in line and current_frame_hex:
                try:
                    frame = bytes.fromhex(current_frame_hex)
                    
                    if len(frame) >= RTT_OFFSET + 55:
                        # Extragem cei 55 de octeți ai RTT-ului
                        rtt_bytes = frame[RTT_OFFSET : RTT_OFFSET+55]
                        
                        # Pentru a trata cu ușurință câmpurile de 10 biți, convertim blocul RTT într-un șir binar
                        # Asigurăm formatarea fixă de 8 biți per octet (ex: '01011010')
                        rtt_bits = "".join(f"{b:08b}" for b in rtt_bytes)
                        
                        # --- 1. EPS (192 biți / 24 octeți) ---
                        # Datele pe 16 biți în FUNcube sunt de obicei Little Endian, dar transmise bit cu bit
                        # Notă: Dacă valorile convertite par incorecte, trebuie inversate ordinea byților.
                        # Pentru simplitate, mai jos procesăm asertând o curgere continuă (Big Endian logic).
                        eps_pv1 = extract_bits(rtt_bits, 0, 16) / 1000.0
                        eps_pv2 = extract_bits(rtt_bits, 16, 16) / 1000.0
                        eps_pv3 = extract_bits(rtt_bits, 32, 16) / 1000.0
                        eps_pc_tot = extract_bits(rtt_bits, 48, 16) / 1000.0 # mA -> A
                        eps_batt_v = extract_bits(rtt_bits, 64, 16) / 1000.0
                        eps_sys_c = extract_bits(rtt_bits, 80, 16) / 1000.0
                        
                        eps_boost_t1 = to_signed_8bit(extract_bits(rtt_bits, 128, 8))
                        eps_batt_t = to_signed_8bit(extract_bits(rtt_bits, 152, 8))
                        
                        # --- 2. BOB (100 biți) - Senzori non-aliniați ---
                        bob_start = 192
                        # Senzori solari (Raw - necesită ecuații cu unghiuri)
                        sun_x = extract_bits(rtt_bits, bob_start, 10)
                        sun_y = extract_bits(rtt_bits, bob_start+10, 10)
                        sun_z = extract_bits(rtt_bits, bob_start+20, 10)
                        
                        # Temperaturi panouri solare (Raw 10-biți - necesită ecuația termistorului polinomial)
                        # Pentru a afla formula termistorului: https://github.com/daniestevez/gr-satellites
                        panel_t_x_pos = convert_panel_temp(extract_bits(rtt_bits, bob_start+30, 10))
                        panel_t_x_neg = convert_panel_temp(extract_bits(rtt_bits, bob_start+40, 10))
                        panel_t_y_pos = convert_panel_temp(extract_bits(rtt_bits, bob_start+50, 10))
                        panel_t_y_neg = convert_panel_temp(extract_bits(rtt_bits, bob_start+60, 10))
                        
                        raw_3v3_bus_v = extract_bits(rtt_bits, bob_start+70, 10)
                        raw_3v3_bus_c = extract_bits(rtt_bits, bob_start+80, 10)
                        raw_5v0_bus_v = extract_bits(rtt_bits, bob_start+90, 10)

                        # Conversia în unități inginerești
                        # Multiplicatorul pentru 3.3V este 4 (din referința AMSAT: 820 * 4 = 3280 mV)
                        bob_3v3_bus_voltage_V = (raw_3v3_bus_v * 4.0) / 1000.0
                        
                        # Curentul și tensiunea de 5V folosesc coeficienți de scalare specifici panoului
                        bob_3v3_bus_current_mA = raw_3v3_bus_c # Se raportează de obicei direct în mA
                        bob_5v0_bus_voltage_V = raw_5v0_bus_v / 1000.0
                        
                        # --- 3. RF (48 biți) ---
                        rf_start = bob_start + 100 # 292
                        
                        # Extragere pe 8 biți
                        rf_doppler_raw = extract_bits(rtt_bits, rf_start, 8)
                        rf_rssi_raw = extract_bits(rtt_bits, rf_start+8, 8)
                        raw_rf_temp = extract_bits(rtt_bits, rf_start+16, 8)
                        raw_rf_rx_current = extract_bits(rtt_bits, rf_start+24, 8)
                        raw_rf_tx_3v3_current = extract_bits(rtt_bits, rf_start+32, 8)
                        raw_rf_tx_5v0_current = extract_bits(rtt_bits, rf_start+40, 8)

                        # Conversia în unități inginerești
                        # Doppler și RSSI sunt utilizate frecvent ca valori index raw în dashboard-uri
                        rf_doppler = rf_doppler_raw
                        rf_rssi = rf_rssi_raw
                        
                        # Temperaturile RF și curenții folosesc coeficienți dedusi (ex. mA = raw * coeficient)
                        # Valorile de mai jos sunt aproximări liniare standard; le poți ajusta fin comparând cu gr-satellites
                        rf_temp_C = raw_rf_temp * 0.25 # Exemplu de scalare
                        rf_rx_current_mA = raw_rf_rx_current * 0.5
                        rf_tx_3v3_current_mA = raw_rf_tx_3v3_current * 0.5
                        rf_tx_5v0_current_mA = raw_rf_tx_5v0_current * 0.5

                        # --- 4. PA (32 biți) ---
                        # Începe la bitul 340 (după cei 48 de biți ai modulului RF)
                        pa_start = rf_start + 48 
                        
                        raw_pa_rev_pwr = extract_bits(rtt_bits, pa_start, 8)
                        raw_pa_fwd_pwr = extract_bits(rtt_bits, pa_start+8, 8)
                        raw_pa_board_temp = extract_bits(rtt_bits, pa_start+16, 8)
                        raw_pa_board_curr = extract_bits(rtt_bits, pa_start+24, 8)

                        # Conversia în unități inginerești
                        # Deoarece documentația nu specifică formulele, vom păstra valorile ca indici aproximativi (sau le poți ajusta comparând cu referința AMSAT)
                        pa_reverse_power = raw_pa_rev_pwr 
                        pa_forward_power = raw_pa_fwd_pwr
                        pa_board_temp_C = raw_pa_board_temp # Ajustează dacă folosește un termistor specific
                        pa_board_current_mA = raw_pa_board_curr 

                        # --- 5. ANTS (20 biți) ---
                        # Începe la bitul 372 (după cei 32 de biți ai PA)
                        ants_start = pa_start + 32 
                        
                        raw_ants_temp_0 = extract_bits(rtt_bits, ants_start, 8)
                        raw_ants_temp_1 = extract_bits(rtt_bits, ants_start+8, 8)
                        
                        # Extragerea fiecărui bit de deschidere a antenei
                        ants_deploy_0 = bool(extract_bits(rtt_bits, ants_start+16, 1))
                        ants_deploy_1 = bool(extract_bits(rtt_bits, ants_start+17, 1))
                        ants_deploy_2 = bool(extract_bits(rtt_bits, ants_start+18, 1))
                        ants_deploy_3 = bool(extract_bits(rtt_bits, ants_start+19, 1))
                        
                        # --- 4. SW (Stare Software - extragem doar modul de eclipsă și siguranță) ---
                        sw_start = 292 + 48 + 32 + 20 # Sărim RF, PA, ANTS = Bitul 392
                        in_eclipse = extract_bits(rtt_bits, sw_start + 43, 1)
                        in_safe_mode = extract_bits(rtt_bits, sw_start + 44, 1)

                        frame_timestamp = base_time + datetime.timedelta(seconds=frame_count * 5)
                        frame_count += 1

                        telemetry_data.append({
                            "timestamp": frame_timestamp.isoformat(),
                            "eps_photo_voltage_1_V": round(eps_pv1, 3),
                            "eps_photo_voltage_2_V": round(eps_pv2, 3),
                            "eps_photo_voltage_3_V": round(eps_pv3, 3),
                            "battery_voltage_mV": round(eps_batt_v * 1000, 1),
                            "system_current_mA": round(eps_sys_c * 1000, 1),
                            "battery_temp_C": eps_batt_t,
                            "eps_boost_temp_1_C": eps_boost_t1,
                            "bob_sun_x_raw": sun_x,
                            "bob_sun_y_raw": sun_y,
                            "bob_sun_z_raw": sun_z,
                            "paneltemp_xp": panel_t_x_pos,
                            "paneltemp_xn": panel_t_x_neg,
                            "paneltemp_yp": panel_t_y_pos,
                            "paneltemp_yn": panel_t_y_neg,
                            "bob_3v3_bus_mA": bob_3v3_bus_current_mA,
                            "bob_3v3_bus_v": bob_3v3_bus_voltage_V,
                            "rf_doppler": rf_doppler,
                            "rf_rssi": rf_rssi,
                            "pa_reverse_power_raw": pa_reverse_power,
                            "pa_forward_power_raw": pa_forward_power,
                            "pa_board_temp_C": pa_board_temp_C,
                            "pa_board_current_mA": pa_board_current_mA,
                            "ants_temp_0_raw": raw_ants_temp_0,
                            "ants_temp_1_raw": raw_ants_temp_1,
                            "ants_deploy_0": ants_deploy_0,
                            "ants_deploy_1": ants_deploy_1,
                            "ants_deploy_2": ants_deploy_2,
                            "ants_deploy_3": ants_deploy_3,
                            "in_eclipse": bool(in_eclipse),
                            "sw_in_safe_mode": bool(in_safe_mode)
                        })
                except Exception as e:
                    print(f"Eroare la parsarea cadrului: {e}")
                
                current_frame_hex = ""

    return telemetry_data

def parse_satnogs_hex_blocks(file_path):
    telemetry_data = []
    base_time = datetime.datetime.now()
    frame_count = 0

    with open(file_path, 'r') as f:
        content = f.read()

    blocks = [b.strip() for b in content.split('\n\n') if b.strip()]

    for block in blocks:
        hex_string = block.replace('\n', ' ').replace(' ', '')
        try:
            frame = bytes.fromhex(hex_string)
            if len(frame) >= 1 + 55:
                rtt_bytes = frame[1:1+55]
                rtt_bits = "".join(f"{b:08b}" for b in rtt_bytes)

                eps_batt_v = extract_bits(rtt_bits, 64, 16) / 1000.0
                eps_sys_c = extract_bits(rtt_bits, 80, 16) / 1000.0
                eps_batt_t = to_signed_8bit(extract_bits(rtt_bits, 152, 8))

                frame_timestamp = base_time + datetime.timedelta(seconds=frame_count * 5)
                frame_count += 1

                telemetry_data.append({
                    "timestamp": frame_timestamp.isoformat(),
                    "battery_voltage_mV": round(eps_batt_v * 1000, 1),
                    "system_current_mA": round(eps_sys_c * 1000, 1),
                    "battery_temp_C": eps_batt_t
                })
        except Exception as e:
            print(f"Eroare la pachet: {e}")

    return telemetry_data

parsed_records = parse_satnogs_hex_blocks("decoded_frames.txt")
for i, record in enumerate(parsed_records[:3]):
    print(f"Frame {i+1}: {json.dumps(record, indent=2)}")

if parsed_records:
    df = pd.DataFrame(parsed_records)
    df.to_csv("telemetry.csv", index=False)
    print(f"\nSalvat {len(parsed_records)} inregistrari in telemetry.csv")