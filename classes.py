import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
import librosa

class FileBrowser:
    global player
    def __init__(self, parent = None):
        self.parent = parent
        # Define the instruments and volumes
        
      
    def browse_file(self, mode):
        if mode == 'music':
            file_path, _ = QFileDialog.getOpenFileName(directory= "D:/Signal-Equalizer-DSP", filter= " wav files (*.wav)")
            signal, sampling_rate= librosa.load(file_path, sr= None)
            print(f"Signal path: {file_path}")
            return signal, sampling_rate

class Spectrogram(QWidget):
    def __init__(self, signal=None):
        super().__init__()

        if signal == None: # The case of uniform range mode
            self.magnitudes = [1] * 10
            self.fs = 210
            self.t = np.arange(0, 1, 1 / self.fs)
            self.signal = self.generateSignal(self.magnitudes)
        else: # Other modes
            self.signal = signal
            self.magnitudes = [1] * 4
            self.fs = 5000
            
        layout = QVBoxLayout()
        self.fig, self.ax = plt.subplots(figsize=(8, 6))   # Set up the matplotlib plot for the spectrogram
        layout.addWidget(self.fig.canvas)

        self.cax = None         # Needed for initial colorbar creation
        self.plotSpectrogram(self.signal, self.fs, self.ax, self.cax)
        
        self.setLayout(layout)
        self.show()

    def plotSpectrogram(self, signal, fs, ax, cax):
        #The signal is divided into overlapping segments, and for each segment, an FFT is computed
        nperseg = 128  # The length of each segment for the FFT
        nfft = 1024  # Number of points for zero-padding the FFT (determines length of FFT to improve frequency resolution)
        fSpectro, tSpectro, spectralDensity = spectrogram(signal, fs, nperseg=nperseg, nfft=nfft, window='hann', noverlap=nperseg//2) # hann window function is applied to each segment of the signal before the FFT to minimize the impact of segmenting 

        ax.clear()
        cax = ax.pcolormesh(tSpectro, fSpectro, 10 * np.log10(spectralDensity), shading='auto', cmap='inferno') # use dB scale for intensity
        ax.set_ylabel("Frequency [Hz]")
        ax.set_xlabel("Time [sec]")
        ax.set_ylim(0, 0.5 * self.fs)  # Limit the y-axis to 1/2 the frequency sampling

        # Add the color bar (only once after the first plot)
        if cax is not None:
            # Create the colorbar
            if not hasattr(ax, 'colorbar'):  # If the colorbar doesn't already exist
                ax.figure.colorbar(cax, ax=ax, label='Magnitude (dB)')
                ax.colorbar = True  # Mark the colorbar as created
    
        plt.draw()
    
    def update(self, magnitudes): # Update the spectrogram after slider value changes
        self.magnitudes = magnitudes
        self.signal = self.generateSignal(self.magnitudes)
        self.plotSpectrogram(self.signal, self.fs, self.ax, self.cax)
    
    def showSpectrogram(self):
        self.show()
    
    def hideSpectrogram(self):
        self.hide()

    def generateSignal(self, magnitudes): # Generate sin signal for uniform range mode
        signal = 0
        loopCounter = 0
        for freq in range(10, 110, 10):
            signal += magnitudes[loopCounter] * np.sin(2 * np.pi * freq * self.t)
            loopCounter += 1
        
        return signal