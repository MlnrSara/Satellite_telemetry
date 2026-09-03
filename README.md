# Satellite telemetry decoder with dashboard

Prerequisites: gr-satellites installed, clone https://github.com/daniestevez/satellite-recordings.git (for the wav file)

In order to generate the telemetry.csv file, use `gr_satellites FUNcube-1 --wavfile satellite-recordings/ao73.wav --samp_rate 48e3 | python3 stream_collector.py`

If you want to see the dashboard, use `streamlit run app.py`