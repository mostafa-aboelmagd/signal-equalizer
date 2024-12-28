import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from pyqtgraph import PlotWidget, mkPen
import soundfile as sf



class FFTPlotCanvas(PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plotItem = self.getPlotItem()
        self.plotItem.setMouseEnabled(x=True, y=True)  # Enable zoom and pan in both x and y

        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.max_freq = 0
        self.max_magnitude = 1
        self.log_scale = False  # Linear scale by default

        self.setBackground("w")
        self.curve = self.plot(pen=mkPen(color="r", width=2))

    def plot_frequency_domain(self, signal, sample_rate=44100):
        if signal is None or len(signal) == 0:
            self.clear()
            return
        
        # Compute FFT
        N = len(signal)
        freq_components = np.fft.fft(signal)
        freq_magnitude = np.abs(freq_components[:N // 2])
        freq_magnitude_db = 20 * np.log10(freq_magnitude + 1e-12)
        freq_bins = np.fft.fftfreq(N, d=1 / sample_rate)[:N // 2]

        # Update max frequency and amplitude
        self.max_freq = max(freq_bins)
        self.max_magnitude = max(freq_magnitude)

        # Plot based on the scale
        if self.log_scale:
            self.plotItem.setLogMode(x=True, y=False)
            self.curve.setData(freq_bins, freq_magnitude_db)
        else:
            self.plotItem.setLogMode(x=False, y=False)
            self.curve.setData(freq_bins, freq_magnitude)
        
        # Set axis limits based on the data
        self.x_min, self.x_max = 0, self.max_freq
        self.y_min, self.y_max = 0, self.max_magnitude

        self.plotItem.setLimits(
            xMin=self.x_min, xMax=self.x_max,
            yMin=self.y_min, yMax=self.y_max
        )
        self.plotItem.setXRange(self.x_min, self.x_max)
        self.plotItem.setYRange(self.y_min, self.y_max)

    def toggle_log_scale(self):
        self.log_scale = not self.log_scale
        self.plotItem.setLogMode(x=self.log_scale, y=False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio Signal Analysis - Time & Frequency Domain")
        self.setGeometry(200, 200, 800, 600)

        # Initialize variables
        self.sample_rate = 44100  # Default sample rate
        self.signal = np.zeros(44100)  # Default empty signal (1 second of silence)

        # Set up UI components
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout(self.main_widget)

        self.canvas = FFTPlotCanvas()
        layout.addWidget(self.canvas)

        self.plot_freq_button = QPushButton("Plot Frequency Domain")
        self.plot_freq_button.clicked.connect(self.plot_frequency_domain)
        layout.addWidget(self.plot_freq_button)

        self.load_audio_button = QPushButton("Load Audio File")
        self.load_audio_button.clicked.connect(self.load_audio)
        layout.addWidget(self.load_audio_button)

    def plot_frequency_domain(self):
        self.canvas.plot_frequency_domain(self.signal, self.sample_rate)

    def load_audio(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.flac *.ogg *.mp3);;All Files (*)")
        if file_name:
            try:
                # Load audio file
                self.signal, self.sample_rate = sf.read(file_name)
                
                # If stereo, convert to mono
                if self.signal.ndim > 1:
                    self.signal = np.mean(self.signal, axis=1)
                
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
