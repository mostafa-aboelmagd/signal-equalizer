import sys
import numpy as np
import soundfile as sf
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class FFTPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

        # Initialize zoom variables
        self.x_min = None
        self.x_max = None
        self.zoom_factor = 0.1  # 10% zoom
    
    # Hide the canvas from within the FFTPlotCanvas class
    def hideCanvas(self):
        self.setVisible(False)  # Hides the canvas

    # Show the canvas from within the FFTPlotCanvas class
    def showCanvas(self):
        self.setVisible(True)  # Shows the canvas

    def plot_time_domain(self, signal, sample_rate):
        self.ax.clear()
        t = np.linspace(0, len(signal) / sample_rate, len(signal))
        self.ax.plot(t, signal)
        self.ax.set_title("Time Domain Signal")
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)
        self.draw()

    def plot_frequency_domain(self, signal, sample_rate):
        self.ax.clear()
        # Compute FFT
        N = len(signal)
        freq_components = np.fft.fft(signal)
        freq_magnitude = np.abs(freq_components[:N // 2])
        freq_bins = np.fft.fftfreq(N, d=1 / sample_rate)[:N // 2]

        self.ax.plot(freq_bins, freq_magnitude, 'r')
        self.ax.set_title("Frequency Domain Signal")
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("Magnitude")
        self.ax.grid(True)

        # Set initial limits for zooming
        self.x_min, self.x_max = self.ax.get_xlim()
        self.draw()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming in and out."""
        if self.x_min is None or self.x_max is None:
            return

        zoom_in = event.angleDelta().y() > 0  # Scroll up for zoom in, down for zoom out
        range_span = self.x_max - self.x_min
        zoom_amount = self.zoom_factor * range_span

        if zoom_in:
            self.x_min += zoom_amount
            self.x_max -= zoom_amount
        else:
            self.x_min -= zoom_amount
            self.x_max += zoom_amount

        # Apply the new x-axis limits
        self.ax.set_xlim(self.x_min, self.x_max)
        self.draw()

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

        self.canvas = FFTPlotCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)

        self.plot_time_button = QPushButton("Plot Time Domain")
        self.plot_time_button.clicked.connect(self.plot_time_domain)
        layout.addWidget(self.plot_time_button)

        self.plot_freq_button = QPushButton("Plot Frequency Domain")
        self.plot_freq_button.clicked.connect(self.plot_frequency_domain)
        layout.addWidget(self.plot_freq_button)

        self.load_audio_button = QPushButton("Load Audio File")
        self.load_audio_button.clicked.connect(self.load_audio)
        layout.addWidget(self.load_audio_button)

    def plot_time_domain(self):
        self.canvas.plot_time_domain(self.signal, self.sample_rate)

    def plot_frequency_domain(self):
        self.canvas.plot_frequency_domain(self.signal, self.sample_rate)

    def load_audio(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.flac *.ogg *.mp3);;All Files (*)")
        if file_name:
            try:
                # Load audio file
                self.signal, self.sample_rate = sf.read(file_name)
                
                # If stereo, take only one channel
                if self.signal.ndim > 1:
                    self.signal = self.signal[:, 0]
                
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
