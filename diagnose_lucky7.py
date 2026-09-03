import wave
import numpy as np
from scipy import signal as scipy_signal

def diagnose_audio(wav_file):
    try:
        with wave.open(wav_file, 'rb') as f:
            params = f.getparams()
            frames = f.readframes(params.nframes)
        
        audio = np.frombuffer(frames, dtype=np.int16).astype(float)
        sample_rate = params.framerate
        duration = len(audio) / sample_rate
        
        print("=== AUDIO SIGNAL QUALITY ===\n")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Duration: {duration:.2f} seconds")
        
        print(f"\n=== AMPLITUDE STATISTICS ===")
        print(f"Peak amplitude: {np.max(np.abs(audio)):.0f}")
        print(f"Mean amplitude: {np.mean(np.abs(audio)):.2f}")
        print(f"Std deviation: {np.std(audio):.2f}")
        peak_to_mean = np.max(np.abs(audio)) / (np.std(audio) + 1e-10)
        print(f"Signal-to-Noise Ratio: {peak_to_mean:.1f}:1")
        
        if peak_to_mean < 3:
            print("  ⚠️  WARNING: Very low SNR - recording is mostly noise!")
        elif peak_to_mean < 5:
            print("  ⚠️  WARNING: Marginal SNR - decoding may be difficult")
        elif peak_to_mean > 20:
            print("  ✓ Good SNR - signal should decode")
        
        # Frequency analysis
        print(f"\n=== FREQUENCY CONTENT ===")
        window_size = min(sample_rate * 5, len(audio))
        fft = np.abs(np.fft.rfft(audio[:window_size]))
        freqs = np.fft.rfftfreq(window_size, 1/sample_rate)
        
        peaks, props = scipy_signal.find_peaks(fft, height=np.max(fft)*0.05)
        if len(peaks) > 0:
            top_indices = np.argsort(props['peak_heights'])[-10:][::-1]
            print("Top 10 frequency peaks:")
            for i, idx in enumerate(top_indices):
                print(f"  {i+1}. {freqs[peaks[idx]]/1000:.1f} kHz (magnitude: {props['peak_heights'][idx]:.0f})")
        else:
            print("❌ No significant frequency peaks found!")
            print("This means the recording is pure noise or completely silent.")
        
        print(f"\n=== ANALYSIS ===")
        print("Lucky-7 uses 4.8k FSK with ~2 kHz tone separation")
        print("Expected to see 2 distinct tones in the spectrum above.")
        
        return peak_to_mean, len(peaks)
        
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0

if __name__ == "__main__":
    import sys
    wav_file = sys.argv[1] if len(sys.argv) > 1 else "lucky-second.wav"
    snr, num_peaks = diagnose_audio(wav_file)
    
    print(f"\n=== CONCLUSION ===")
    if snr < 3 and num_peaks < 5:
        print("❌ This recording appears to be noise-only.")
        print("   The Lucky-7 satellite signal is not present or too weak.")
    elif num_peaks < 2:
        print("⚠️  Cannot detect FSK tones. Possible issues:")
        print("   • Recording was in BPSK or USB mode instead of FSK")
        print("   • Center frequency was way off")
        print("   • OGG compression destroyed the signal")