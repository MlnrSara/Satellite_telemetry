# Satellite telemetry decoder with dashboard

Prerequisites: gr-satellites installed, clone https://github.com/daniestevez/satellite-recordings.git (for the wav file)

In order to generate the telemetry.csv file, use `gr_satellites FUNcube-1 --wavfile satellite-recordings/ao73.wav --samp_rate 48e3 | python3 stream_collector.py`

If you want to see the dashboard, use `streamlit run app.py`


## Current Status (Sept 5, 2026)
- Base pipeline (.wav -> gr_satellites -> stream_collector -> dashboard) is working
- gr_satellites does NOT decode real SatNOGS recordings locally (good SNR, waterfall shows 
  a clear signal, but output is completely empty even with --hexdump and --f_offset) - root cause still unknown
- Working alternative: pull already-decoded packets from SatNOGS (the "Data" tab on the 
  observation page) and process them with parse_satnogs_hex_blocks() in parser.py
- parse_satnogs_hex_blocks() currently extracts only 3 fields (battery, current, temp) - needs to be extended with the rest