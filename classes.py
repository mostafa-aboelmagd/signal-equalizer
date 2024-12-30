import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.signal import spectrogram
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer
from pathlib import Path
import soundfile as sf
import pandas as pd
import librosa
import os

class FileBrowser:
    global player
    def __init__(self, parent = None):
        self.parent = parent
        self.player = QMediaPlayer()
        self.signal = None
        self.sampling_rate = None

    def browse_file(self, mode = "wav"):
        try:
            if mode == "ecg":
                file_path, _ = QFileDialog.getOpenFileName(directory="D:/Signal-Equalizer-DSP", filter="CSV files (*.csv)")
                self.fileName = Path(file_path).stem

                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path)

                # Extract the 'time' and 'amplitude' columns
                self.time = df['Time'].values  # The first column contains time values
                self.signal = df['Amplitude'].values  # The second column contains amplitude values

                # Assuming uniform time intervals
                time_deltas = np.diff(self.time)  # Compute differences between consecutive time values
                self.sampling_rate = 1 / np.mean(time_deltas)  # Approximate sampling rate (in Hz)

            else:
                file_path, _ = QFileDialog.getOpenFileName(directory= "D:/Signal-Equalizer-DSP", filter= " wav files (*.wav)")
                self.fileName = Path(file_path).stem
                self.signal, self.sampling_rate = librosa.load(file_path, sr= None)
        except Exception:
            return None, None

        return self.signal, self.sampling_rate
    
    def play_original_signal(self):
        temp_file_path = "temp_original.wav"
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
        else:
            self.player = QMediaPlayer()
            sf.write(temp_file_path, self.signal, self.sampling_rate) # writes to a temporary local file as QMediaPlayer can only recognize them
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_file_path)))
            self.player.play()

    def play_modified_signal(self):
        temp_file_path = "temp_modified.wav"
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
        else:
            self.player = QMediaPlayer()
            sf.write(temp_file_path, self.signal, self.sampling_rate)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_file_path)))
            self.player.play()

class Spectrogram(QWidget):
    def __init__(self, signal=None, fs=None):
        super().__init__()

        if signal is None:  # The case of uniform range mode
            self.magnitudes = [1] * 10
            self.fs = 210
            self.t = np.arange(0, 1, 1 / self.fs)
            self.signal = self.generateSignal(self.magnitudes)
        else:  # Other modes
            self.signal = signal
            self.magnitudes = [1] * 4
            self.fs = fs

        # Set up the main layout
        self.layout = QVBoxLayout(self)

        # Set up the Matplotlib figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(8, 6))  # Create the figure
        self.canvas = FigureCanvas(self.fig)  # Create the canvas from the figure
        self.layout.addWidget(self.canvas)  # Add the canvas to the layout

        self.cax = None  # Needed for initial colorbar creation
        self.plotSpectrogram(self.signal, self.fs, self.ax, self.cax)

        # Set layout for the Spectrogram QWidget
        self.setLayout(self.layout)

        # Timer to delay updates for smoother transitions
        self.updateTimer = QTimer(self)
        self.updateTimer.setSingleShot(True)  # Make sure it only fires once even if it was fired multiple times before ending
        self.updateTimer.timeout.connect(self.redraw_spectrogram)

    def plotSpectrogram(self, signal, fs, ax = None, cax = None):
        ax = self.ax
        if fs != 210:
            self.signal = signal
            self.magnitudes = [1] * 4
            self.fs = fs
        
        else:
            if len(self.magnitudes) != 10:
                self.magnitudes = [1] * 10
                self.fs = 210
                self.t = np.arange(0, 1, 1 / self.fs)
                self.signal = self.generateSignal(self.magnitudes)
        
        """The signal is divided into overlapping segments, and for each segment, an FFT is computed"""
        nperseg = 128  # The length of each segment for the FFT
        nfft = 1024  # Number of points for zero-padding the FFT (determines length of FFT to improve frequency resolution)
        fSpectro, tSpectro, spectralDensity = spectrogram(self.signal, self.fs, nperseg=nperseg, nfft=nfft, window='hann', noverlap=nperseg//2)  # hann window function is applied to each segment of the signal before the FFT to minimize the impact of segmenting

        ax.clear()  # Clear the existing plot
        cax = ax.pcolormesh(tSpectro, fSpectro, 10 * np.log10(spectralDensity + 1e-12), shading='auto', cmap='inferno')  # Use dB scale for intensity
        ax.set_ylabel("Frequency [Hz]")
        ax.set_xlabel("Time [sec]")
        ax.set_ylim(0, 0.5 * self.fs)  # Limit the y-axis to 1/2 the frequency sampling

        # Add the color bar (only once after the first plot)
        if cax is not None:
            # Create the colorbar
            if not hasattr(ax, 'colorbar'):  # If the colorbar doesn't already exist
                ax.figure.colorbar(cax, ax=ax, label='Magnitude (dB)')
                ax.colorbar = True  # Mark the colorbar as created

        self.canvas.draw()  # Redraw the canvas to reflect the updated plot

    def update(self, signal, magnitudes):  # Update the spectrogram after slider value changes
        if signal is None:
            self.magnitudes = magnitudes
            self.signal = self.generateSignal(self.magnitudes)
        else:
            self.signal = signal
        
        # Start the timer to update the spectrogram after a short delay
        self.updateTimer.start(150)  # 150ms delay before redrawing

    def redraw_spectrogram(self):
        self.plotSpectrogram(self.signal, self.fs, self.ax, self.cax)


    def showSpectrogram(self):
        """Show the spectrogram widget in the main window"""
        self.show()

    def hideSpectrogram(self):
        """Hide the spectrogram widget"""
        self.hide()

    def generateSignal(self, magnitudes):  # Generate sin signal for uniform range mode
        signal = 0
        loopCounter = 0
        for freq in range(10, 110, 10):
            signal += magnitudes[loopCounter] * np.sin(2 * np.pi * freq * self.t)
            loopCounter += 1

        return signal