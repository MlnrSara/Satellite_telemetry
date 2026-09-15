# Satellite telemetry decoder with dashboard

Prerequisites: gr-satellites installed, clone https://github.com/daniestevez/satellite-recordings.git (for the wav file)

In order to generate the telemetry.csv file, use `gr_satellites FUNcube-1 --wavfile satellite-recordings/ao73.wav --samp_rate 48e3 | python3 stream_collector.py`

If you want to see the dashboard, use `streamlit run app.py`


# Satellite telemetry decoder with dashboard

Prerequisites: gr-satellites installed, clone https://github.com/daniestevez/satellite-recordings.git (for the wav file)

In order to generate the telemetry.csv file, use `gr_satellites FUNcube-1 --wavfile satellite-recordings/ao73.wav --samp_rate 48e3 | python3 stream_collector.py`

If you want to see the dashboard, use `streamlit run app.py`

## CubeSat Telemetry — FUNcube-1 (AO-73)

Decodes FUNcube-1 telemetry into engineering values (battery voltage, current,
temperature) and visualizes them on a live dashboard.

### Pipeline

gr_satellites  -->  stream_collector.py  -->  telemetry.csv  -->  app.py (Streamlit dashboard)
(decodes radio      (collects & structures
 signal)              packets into CSV rows)

### Prerequisites

- Miniconda (recommended over full Anaconda — smaller, faster to set up)
- GNU Radio + gr-satellites, installed via conda-forge:
  conda install -c conda-forge gnuradio
  conda install -c conda-forge gnuradio-satellites
- Python packages: pip install streamlit pandas

### Running on a clean test recording

git clone https://github.com/daniestevez/satellite-recordings.git
gr_satellites FUNcube-1 --wavfile satellite-recordings/ao73.wav --samp_rate 48e3 | python stream_collector.py
streamlit run app.py

This produces telemetry.csv and generates a working dashboard end-to-end.

### Packet structure

Each FUNcube-1 telemetry packet is 55 bytes of structured binary data (the RTT
block), with fixed bit offsets per subsystem:

EPS (power) -> BOB (sensors) -> RF -> PA -> ANTS -> SW

Example: bits 64–80 encode battery voltage; divide by 1000 to get Volts.
Some fields (e.g. panel temperatures) require a Steinhart-Hart thermistor
equation rather than a simple linear scale — see convert_panel_temp() in
parser.py.

### Known issue: gr_satellites does not decode real SatNOGS recordings locally

The pipeline above works perfectly on the clean test .wav file, but produces
empty output on real SatNOGS observation recordings — and it is not an
obviously bad signal:

- Signal-to-noise ratio on the real recording: 14.9:1 (good, not noise)
- SatNOGS waterfall for the observation shows a clear, visible BPSK transmission
- Output is empty even with --hexdump and manual --f_offset adjustments
  near 0 Hz

Leading theory (not yet fully confirmed): gr_satellites defaults to
searching for the signal around a --f_offset of 1500 or 12000 Hz, not 0.
Frequency analysis on the real recording showed peaks near 12.6 kHz — right
next to that 12000 Hz default — suggesting the offset search range, not the
signal itself, may be the actual issue. Next step: test
--f_offset 12600, and if needed, widen the sync loop bandwidths
(--fll_bw, --costas_bw).

### Workaround: decoded packets from SatNOGS

While the root cause above is unresolved, SatNOGS itself already decodes
packets from each observation and publishes them as raw hex on the
observation's page (the "Data" tab). parser.py includes
parse_satnogs_hex_blocks(), which reads those hex blocks directly and
bypasses gr_satellites locally entirely.

To use it:
1. On the observation page, click "Load All Data" and copy the hex blocks
   into a local file decoded_frames.txt (one blank line between blocks)
2. Run:
   python parser.py
   This calls parse_satnogs_hex_blocks("decoded_frames.txt") and writes
   telemetry.csv
3. Run streamlit run app.py to view the dashboard

Current limitation: parse_satnogs_hex_blocks() currently extracts only
3 fields (battery voltage, current, temperature). The hex structure is
understood well enough to extend it to the rest of the telemetry frame
(panel temperatures, RF/PA values, eclipse/safe-mode flags), using the same
bit-offset logic already implemented in parse_funcube_frames().

### Next steps

- Confirm and fix the root cause of the gr_satellites / SatNOGS decoding
  failure (frequency offset is the current leading theory)
- Extend parse_satnogs_hex_blocks() to the full telemetry frame
- Automate retrieval of new SatNOGS observations so the dashboard updates
  itself daily, without manual downloads

### Lessons learned

- Environment setup (GNU Radio + gr-satellites on Windows via conda) took
  longer than the decoding logic itself
- A tool passing on a clean demo file does not guarantee it will behave the
  same way on real-world recordings
- Reading tool documentation carefully — including default parameter values
  — matters as much as trial-and-error debugging
