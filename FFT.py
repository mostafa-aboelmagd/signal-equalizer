import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from pyqtgraph import PlotWidget, mkPen
import soundfile as sf

class FFTPlotCanvas(PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plotItem = self.getPlotItem()
        self.plotItem.setMouseEnabled(x=True, y=True)

        self.setBackground("w")
        self.plotItem.setLabel("left", "Amplitude (dB)")
        self.plotItem.setLabel("bottom", "Frequency (Hz)")
        self.curve = self.plot(pen=mkPen(color="r", width=2))

        self.audiogram_mode = False  # Start in original frequency domain mode

    def plot_frequency_domain(self, signal, sample_rate, modified_components = None, frequency_bins = None, length = None):
        if modified_components is None:
            N = len(signal)
            freq_components = np.fft.fft(signal)
            freq_magnitude = np.abs(freq_components[:N // 2])
            freq_magnitude_db = 20 * np.log10(freq_magnitude + 1e-12)
            freq_bins = np.fft.fftfreq(N, d=1 / sample_rate)[:N // 2]
        else:
            freq_components = modified_components
            freq_magnitude = np.abs(freq_components[:length//2])
            freq_magnitude_db = 20 * np.log10(freq_magnitude + 1e-12)
            freq_bins = frequency_bins[:length // 2]



        if self.audiogram_mode:
            # Audiogram view: Limit frequencies to 250–8000 Hz and invert dB scale
            valid_indices = (freq_bins >= 0) & (freq_bins <= 8000)
            freq_bins = freq_bins[valid_indices]
            freq_magnitude_db = freq_magnitude_db[valid_indices]

            self.plotItem.setLabel("left", "(dB)")
            self.plotItem.getViewBox().setLogMode(True, False)  
            self.curve.setData(freq_bins, -freq_magnitude_db)  # Invert dB for audiogram
        else:
            # Original frequency domain view
            self.plotItem.setLabel("left", "Amplitude")
            self.plotItem.getViewBox().setLogMode(False, False)  # Linear frequency scale
            self.curve.setData(freq_bins, freq_magnitude)
        self.plotItem.setLabel("bottom", "Frequency (Hz)")

        self._set_axis_limits(freq_bins, freq_magnitude if not self.audiogram_mode else freq_magnitude_db)
    
    def _set_axis_limits(self, freq_bins, magnitudes):
        x_min, x_max = np.min(freq_bins), np.max(freq_bins)
        y_min, y_max = np.min(magnitudes), np.max(magnitudes)
        margin = 0.05 # Add a small margin for better visibility
        if self.audiogram_mode:
            ymax=y_min - margin * (y_max - y_min)
            ymin=y_max + margin * (y_max - y_min)
        else:
            ymin=y_min - margin * (y_max - y_min)
            ymax=y_max + margin * (y_max - y_min)
            

        self.plotItem.getViewBox().setLimits(
            xMin=x_min - margin * (x_max - x_min),
            xMax=x_max + margin * (x_max - x_min),
            # Invert y-axis for audiogram view
            yMax=ymax,
            yMin=ymin,
        )

    def toggle_audiogram_scale(self):
        self.audiogram_mode = not self.audiogram_mode  
    def clear_frequency_graph(self):
        self.curve.setData([], [])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toggle Audiogram and Frequency Domain")
        self.setGeometry(200, 200, 800, 600)

        self.sample_rate = 44100
        self.signal = np.zeros(44100)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        self.canvas = FFTPlotCanvas()
        layout.addWidget(self.canvas)

        self.toggle_button = QPushButton("Toggle Audiogram View")
        self.toggle_button.clicked.connect(self.toggle_audiogram)
        layout.addWidget(self.toggle_button)

        self.plot_freq_button = QPushButton("Plot Frequency Domain")
        self.plot_freq_button.clicked.connect(self.plot_frequency_domain)
        layout.addWidget(self.plot_freq_button)

        self.load_audio_button = QPushButton("Load Audio File")
        self.load_audio_button.clicked.connect(self.load_audio)
        layout.addWidget(self.load_audio_button)

    def plot_frequency_domain(self):
        self.canvas.plot_frequency_domain(self.signal, self.sample_rate)

    def toggle_audiogram(self):
        self.canvas.toggle_audiogram_scale()
        self.plot_frequency_domain()  # Refresh plot with the new scale

    def load_audio(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.flac *.ogg *.mp3);;All Files (*)")
        if file_name:
            try:
                self.signal, self.sample_rate = sf.read(file_name)
                if len(self.signal.shape) > 1:
                    self.signal = self.signal[:, 1]
                self.signal[:10*self.sample_rate]

                print(f"Loaded {file_name} with sample rate {self.sample_rate} Hz")
            except Exception as e:
                print(f"Failed to load audio: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
