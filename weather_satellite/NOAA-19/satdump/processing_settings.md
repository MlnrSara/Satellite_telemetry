# NOAA-19 SatDump Processing Settings

## Software

- Software: SatDump
- Version: 1.2.2
- Processing mode: Offline Processing

## Pipeline

- Pipeline: NOAA APT
- NOAA Satellite: 19
- Input Level: audio_wav

## Input

The input was the WAV file converted from the original SatNOGS OGG recording.

- Baseband Format: cs16
- Sample Rate: 48 ksps

## Signal Processing Settings

- DC Blocking: Off
- IQ Swap: Off
- Frequency Shift: 0 Hz
- Autocrop Pass: Off
- SDR++ Noise Reduction: On

## Timestamp

The observation start time was manually entered:

2024/05/11 10:19:01 UTC

This corresponds to the beginning of the selected SatNOGS observation.

## Output

The SatDump processing output was saved in:

NOAA19_SatDump

The processing generated APT and AVHRR weather imagery products.

## Processing Procedure

1. Open SatDump.
2. Select Offline Processing.
3. Search for the NOAA pipeline.
4. Select NOAA APT.
5. Select NOAA-19.
6. Select `audio_wav` as the input level.
7. Load the converted WAV recording.
8. Verify the detected baseband format and sample rate.
9. Set the observation start timestamp to `2024/05/11 10:19:01 UTC`.
10. Start the processing.
11. Inspect the generated imagery products.

## Generated Products

The processing generated:

- APT-A.png
- APT-B.png
- AVHRR-2.png
- AVHRR-4.png
- avhrr_3_rgb_10.8um_Thermal_IR.png
- avhrr_3_rgb_10.8um_Thermal_IR_corrected.png

Additional SatDump files included:

- dataset.json
- product.cbor
- raw_sync.png
- raw_unsync.png
