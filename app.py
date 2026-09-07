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
        
        # Forward-fill missing values so the dashboard always has a value to display
        df = df.ffill()
        
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Nu există date încă. Rulați decodorul!")
else:
    # Indicatori superiori (Stare Curentă)
    latest = df.iloc[-1]
    cols = st.columns(5)
    
    # Folosim .get() ca safety net in caz ca in primul pachet lipseste parametrul
    cols[0].metric("Voltaj Baterie", f"{latest.get('battery_voltage_mV', 0) / 1000.0:.2f} V")
    cols[1].metric("Curent Sistem", f"{latest.get('system_current_mA', 0)} mA")
    cols[2].metric("Fotocurent", f"{latest.get('photocurrent_mA', 0)} mA")
    cols[3].metric("Secvență Pachet", f"{latest.get('seq_number', 'N/A')}")
    cols[4].metric("În Eclipsă", "DA" if latest.get('in_eclipse', False) else "NU")
    
    st.markdown("---")

    # Organizare layout cu Tab-uri pentru lizibilitate
    tab1, tab2, tab3 = st.tabs(["⚡ EPS & Putere", "🌡️ Temperaturi", "📡 Comunicații & RF"])

    with tab1:
        st.subheader("Evoluția Tensiunii, Curentului și Fotocurentului")
        eps_cols = [c for c in ["battery_voltage_mV", "system_current_mA", "photocurrent_mA"] if c in df.columns]
        if eps_cols:
            st.line_chart(df.set_index("timestamp")[eps_cols])
            
        st.subheader("Magistrale de Curent (3.3V & 5V) (mV)")
        bus_cols = [c for c in ["bus_3v3_voltage_mV", "bus_5v_voltage_mV"] if c in df.columns]
        if bus_cols:
            st.line_chart(df.set_index("timestamp")[bus_cols])

    with tab2:
        st.subheader("Temperaturile Panourilor Solare (°C)")
        panel_cols = [c for c in ["paneltemp_xp", "paneltemp_xn", "paneltemp_yp", "paneltemp_yn"] if c in df.columns]
        if panel_cols:
            st.line_chart(df.set_index("timestamp")[panel_cols])
            
        st.subheader("Temperaturile Șasiului (°C)")
        chassis_cols = [c for c in ["tempblackchassis", "tempsilverchassis", "tempblackpanel", "tempsilverpanel"] if c in df.columns]
        if chassis_cols:
            st.line_chart(df.set_index("timestamp")[chassis_cols])

    with tab3:
        st.subheader("Amplificator Radio Frecvență (PA Power)")
        pa_cols = [c for c in ["pa_fwd_pwr", "pa_rev_pwr"] if c in df.columns]
        if pa_cols:
            st.line_chart(df.set_index("timestamp")[pa_cols])
            
        st.subheader("RSSI și Doppler")
        rf_cols = [c for c in ["rx_rssi", "rx_doppler"] if c in df.columns]
        if rf_cols:
            st.line_chart(df.set_index("timestamp")[rf_cols])

    st.markdown("---")
    st.subheader("Istoric Date Tabelare")
    # Inversăm tabelul ca să vedem cele mai noi date primele
    st.dataframe(df.iloc[::-1].head(25), use_container_width=True)