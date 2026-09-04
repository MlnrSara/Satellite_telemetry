import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="FUNcube-1 Telemetry", layout="wide")
st.title("🛰️ FUNcube-1 (AO-73) Telemetry Dashboard")

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv("telemetry.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Nu există date încă. Rulați decodorul!")
else:
    # Indicatori superiori (Stare Curentă)
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Voltaj Baterie", f"{latest['battery_voltage_mV'] / 1000.0:.2f} V")
    col2.metric("Curent Sistem", f"{latest['system_current_mA']} mA")
    col3.metric("Temp Baterie", f"{latest['battery_temp_C']} °C")
    col4.metric("În Eclipsă", "DA" if latest.get('in_eclipse', False) else "NU")
    st.markdown("---")

    # Grafice
    st.subheader("Evoluția Tensiunii și a Curentului")
    st.line_chart(df.set_index("timestamp")[["battery_voltage_mV", "system_current_mA"]])

    panel_cols = [c for c in ["paneltemp_xp", "paneltemp_xn", "paneltemp_yp", "paneltemp_yn"] if c in df.columns]
if panel_cols:
    st.subheader("Temperaturile Panourilor Solare (°C)")
    st.line_chart(df.set_index("timestamp")[panel_cols])
    
    # Tabel de date
    st.subheader("Date Tabelare")
    st.dataframe(df.tail(10))