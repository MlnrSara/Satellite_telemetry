# NOAA-19 Weather Satellite Imagery

## Project Objective

This part of the project focuses on decoding weather satellite imagery from a real satellite recording available through the SatNOGS network.

The selected satellite is NOAA-19. The recording was processed offline using SatDump in order to obtain weather imagery products.

The complete processing chain was:

SatNOGS observation → recorded signal → OGG audio → WAV conversion → SatDump → NOAA APT decoding → weather imagery

---

## Satellite

- Satellite: NOAA-19
- NORAD ID: 33591
- Signal: NOAA APT
- Frequency: 137.100 MHz

NOAA-19 was selected as the weather satellite for the imagery part of the project because it provides NOAA APT imagery and can be processed using SatDump.

---

## SatNOGS Observations

The recordings used for this project were obtained from the SatNOGS network. In total, 3 distinct observations were processed.

**Observation 1:**
- Observation ID: 9505836
- Satellite: NOAA-19
- NORAD ID: 33591
- Station: 3570 – DC4HF
- Frequency: 137.100 MHz
- Start: 2024-05-11 10:19:01 UTC
- End: 2024-05-11 10:28:37 UTC
- Duration: 576 seconds
- Observation status: Good

**Observation 2:**
- Observation ID: 9518481
- Satellite: NOAA-19
- NORAD ID: 33591
- Frequency: 137.100 MHz
- Start: 2024-05-13 09:55:00 UTC
- Observation status: Good

**Observation 3:**
- Observation ID: 9521580
- Satellite: NOAA-19
- NORAD ID: 33591
- Frequency: 137.100 MHz
- Start: 2024-05-13 09:57:00 UTC
- Observation status: Good

The original recordings were downloaded from the SatNOGS observations.

---

## Input Recording

The SatNOGS recording was downloaded in OGG format.

Original file:

`satnogs_9505836_2024-05-11T10-19-01...ogg`

The OGG recording was converted to WAV format before processing with SatDump.

The WAV file was used as the input recording for the decoding process.

---

## Data Preparation

The original SatNOGS audio recording was converted from OGG to WAV.

Processing chain:

```text
SatNOGS
   ↓
OGG recording
   ↓
WAV conversion
   ↓
WAV input for SatDump
```
---

## SatDump Processing

The recording was processed using:

Software: SatDump
Version: 1.2.2
Pipeline: NOAA APT
Satellite: NOAA-19
Input Level: audio_wav
Baseband Format: cs16
Sample Rate: 48 ksps
Frequency Shift: 0 Hz
DC Blocking: Off
IQ Swap: Off
Autocrop Pass: Off
SDR++ Noise Reduction: On

The observation start time was manually entered as:  2024/05/11 10:19:01 UTC

The output directory used for the processing was:  NOAA19_SatDump

---

## Decoding Process

The WAV recording was loaded into SatDump using the Offline Processing function.

The NOAA APT pipeline was selected and configured for NOAA-19.

SatDump processed the recording and generated several image products from the received NOAA APT signal.

The resulting products include APT and AVHRR imagery.

---

## Dataset Information

SatDump generated a dataset.json file containing information about the processed dataset.

The dataset identifies:

Satellite: NOAA-19
Dataset ID: 5fxaz4
Timestamp: 1715422745.5

The timestamp corresponds to approximately:  2024-05-11 10:19:05.5 UTC

---

## Results

The decoding was successful and produced recognizable weather satellite imagery.

The APT products contain grayscale weather imagery showing cloud structures and geographical areas over Europe and the surrounding region.

The AVHRR products include additional weather imagery, including thermal infrared representations.

Example results are stored in the images/ directory.
