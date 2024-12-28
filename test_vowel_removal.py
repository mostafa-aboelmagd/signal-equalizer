import scipy.fftpack as fft
import numpy as np
import soundfile as sf

# Read the audio file
signal, sampling_rate = sf.read('voice.wav')

# Get the first 10 seconds of the signal
signal = signal[:int(10 * sampling_rate)]

# Perform FFT on the signal
freq = fft.fft(signal)
freqs_bins = fft.fftfreq(len(signal), 1 / sampling_rate)
vowel_formant_ranges = [
        (500, 1100), 
        (1330, 1790),  
]   
# Apply bandstop filter: Zero out frequencies around Formant 2 (1000 Hz to 2000 Hz)
for range in vowel_formant_ranges:
    low_cutoff = range[0]  # Hz
    high_cutoff = range[1]  # Hz
    freq[(np.abs(freqs_bins) >= low_cutoff) & (np.abs(freqs_bins) <= high_cutoff)] = 0
# Perform inverse FFT to get the modified signal
modified_signal = np.real(fft.ifft(freq))

# Write the modified signal to a new file
sf.write('removed.wav', modified_signal, sampling_rate)

    # Define formant frequency ranges for "a" vowels (example ranges)
