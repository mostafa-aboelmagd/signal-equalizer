import parselmouth
import numpy as np
import matplotlib.pyplot as plt

def detect_formants(audio_file):
    # Load the audio file
    sound = parselmouth.Sound(audio_file)

    # Perform formant analysis
    formant = sound.to_formant_burg()

    # Extract formant frequencies
    formant_frequencies = []
    for t in np.arange(0, sound.duration, 0.01):
        formant_frequencies.append([formant.get_value_at_time(i, t) for i in range(1, 4)])

    return np.array(formant_frequencies)

def plot_formants(formant_frequencies):
    # Plot the formant frequencies
    plt.figure()
    for i in range(3):
        plt.plot(formant_frequencies[:, i], label=f'Formant {i+1}')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    audio_file = "VOWEL_A.wav"  # Replace with your audio file
    formant_frequencies = detect_formants(audio_file)
    plot_formants(formant_frequencies)
