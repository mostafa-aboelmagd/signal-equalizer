import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel
from PyQt5.QtCore import Qt
import sys

# Function to generate the signal with adjustable magnitudes
def generate_signal(mag1, mag2):
    fs = 200  # Sampling frequency in Hz
    f1 = 20   # Frequency 1 (20 Hz)
    f2 = 40   # Frequency 2 (40 Hz)
    t = np.arange(0, 1, 1/fs)  # Time vector (1 second)
    
    # Create the signal with adjustable magnitudes for each frequency component
    signal = mag1 * np.sin(2 * np.pi * f1 * t) + mag2 * np.sin(2 * np.pi * f2 * t)
    return signal, t

# Function to plot the spectrogram (without creating new color bar each time)
def plot_spectrogram(signal, fs, ax, cax=None, use_log=True):
    nperseg = 128  # Increase the segment length for better frequency resolution
    nfft = 1024  # Zero-padding for better frequency resolution
    f_spec, t_spec, Sxx = spectrogram(signal, fs, nperseg=nperseg, nfft=nfft, window='hann', noverlap=nperseg//2)
    
    ax.clear()
    
    # Decide whether to use log scale or linear scale for magnitude
    if use_log:
        # Use dB scale for the intensity
        cax = ax.pcolormesh(t_spec, f_spec, 10 * np.log10(Sxx), shading='auto', cmap='inferno')
    else:
        # Use linear scale for the intensity (raw magnitude)
        cax = ax.pcolormesh(t_spec, f_spec, Sxx, shading='auto', cmap='inferno')

    ax.set_ylabel('Frequency [Hz]')
    ax.set_xlabel('Time [sec]')
    ax.set_title('Spectrogram')
    ax.set_ylim(0, 100)  # Limit the y-axis to 100 Hz for clarity

    # Add the color bar (only once after the first plot)
    if cax is not None:
        # Create the colorbar
        if not hasattr(ax, 'colorbar'):  # If the colorbar doesn't already exist
            ax.figure.colorbar(cax, ax=ax, label='Magnitude (dB)' if use_log else 'Intensity (linear)')
            ax.colorbar = True  # Mark the colorbar as created

    plt.draw()

# PyQt5 GUI to control the magnitudes
class SpectrogramApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.fs = 200  # Sampling frequency in Hz
        
        # Initial magnitudes for the two components
        self.mag1 = 2.0  # Magnitude of 20 Hz component
        self.mag2 = 2.0  # Magnitude of 40 Hz component

        self.init_ui()
        
    def init_ui(self):
        # Layout for the application
        layout = QVBoxLayout()

        # Slider for adjusting the magnitude of the 20 Hz component
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setMinimum(0)
        self.slider1.setMaximum(int(self.mag1 * 10))  # Max value based on default signal value
        self.slider1.setValue(int(self.mag1 * 10))  # Set the initial value to the default magnitude
        self.slider1.setTickInterval(1)
        self.slider1.valueChanged.connect(self.update_magnitude)
        layout.addWidget(QLabel('Magnitude of 20 Hz component'))
        layout.addWidget(self.slider1)

        # Slider for adjusting the magnitude of the 40 Hz component
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(int(self.mag2 * 10))  # Max value based on default signal value
        self.slider2.setValue(int(self.mag2 * 10))  # Set the initial value to the default magnitude
        self.slider2.setTickInterval(1)
        self.slider2.valueChanged.connect(self.update_magnitude)
        layout.addWidget(QLabel('Magnitude of 40 Hz component'))
        layout.addWidget(self.slider2)

        # Set up the matplotlib plot for the spectrogram
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        layout.addWidget(self.fig.canvas)

        # Set up the initial signal and plot
        self.signal, self.t = generate_signal(self.mag1, self.mag2)

        # Initial colorbar creation (only once)
        self.cax = None
        plot_spectrogram(self.signal, self.fs, self.ax, self.cax)
        
        self.setLayout(layout)
        self.setWindowTitle('Interactive Spectrogram')
        self.show()
    
    def update_magnitude(self):
        # Get the updated magnitude from slider value and scale it back to the original range
        self.mag1 = self.slider1.value() / 10.0  # Divide by 10 since we multiplied the range by 10
        self.mag2 = self.slider2.value() / 10.0  # Same for the second slider

        # Generate the new signal with updated magnitudes
        self.signal, self.t = generate_signal(self.mag1, self.mag2)
        
        # Update the spectrogram plot (without creating a new colorbar)
        plot_spectrogram(self.signal, self.fs, self.ax, self.cax)

# Main function to run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpectrogramApp()
    sys.exit(app.exec_())
