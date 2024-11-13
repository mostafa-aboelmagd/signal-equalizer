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

        # Initialize zoom and pan variables
        self.x_min = None
        self.x_max = None
        self.log_scale = False
        self.pan_start_x = None  # For panning
        self.zoom_factor = 0.1  # 10% zoom
    
    # Hide the canvas from within the FFTPlotCanvas class
    def hideCanvas(self):
        self.setVisible(False)  # Hides the canvas

    # Show the canvas from within the FFTPlotCanvas class
    def showCanvas(self):
        self.setVisible(True)  # Shows the canvas

        # Enable mouse tracking and set up Matplotlib event handlers
        self.mpl_connect("button_press_event", self.on_mouse_press)
        self.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.mpl_connect("button_release_event", self.on_mouse_release)
        self.mpl_connect("scroll_event", self.on_mouse_scroll)

    def plot_frequency_domain(self, signal, sample_rate):
        self.ax.clear()
        # Compute FFT
        N = len(signal)
        freq_components = np.fft.fft(signal)
        freq_magnitude = np.abs(freq_components[:N // 2])
        freq_bins = np.fft.fftfreq(N, d=1 / sample_rate)[:N // 2]

        # Plot settings
        if self.log_scale:
            self.ax.set_xscale('log')
            if max(freq_bins) > 5000:
                self.ax.set_xlim(left=1, right=5000)  # Set minimum frequency to 20 Hz
            else:
                self.ax.set_xlim(left=1, right=max(freq_bins))
        else:
            self.ax.set_xscale('linear')
            if max(freq_bins) > 5000:
                self.ax.set_xlim(left=0, right=5000)  # Set maximum frequency to 5000 Hz
            else:
                self.ax.set_xlim(left=0, right=max(freq_bins))
        
        self.ax.plot(freq_bins, freq_magnitude, 'r')
        self.ax.set_title("Frequency Domain Signal")
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("Magnitude")
        self.ax.grid(True)

        # Set initial limits for zooming and panning
        self.x_min, self.x_max = self.ax.get_xlim()
        self.draw()

    def on_mouse_press(self, event):
        """Capture the initial x-coordinate when the left mouse button is pressed."""
        if event.button == 1 and event.xdata is not None:  # Left mouse button
            self.pan_start_x = event.xdata

    def on_mouse_move(self, event):
        """Handle mouse drag events for panning left and right."""
        if self.pan_start_x is not None and event.xdata is not None:
            # Calculate the delta to move the plot
            if self.log_scale:
                delta_x = (np.log10(self.pan_start_x) - np.log10(event.xdata))
            else: 
                delta_x = (self.pan_start_x - event.xdata)
            self.pan_start_x = event.xdata

            # Adjust the x-axis limits for panning
            self.x_min += delta_x
            self.x_max += delta_x

            # Ensure limits stay within the valid frequency range
            if self.x_min < 1:
                self.x_min = 1
                self.x_max = (self.x_max - self.x_min)
            if self.x_max > 20000:
                self.x_max = 20000
                self.x_min = 20000 - (self.x_max - self.x_min)

            self.ax.set_xlim(self.x_min, self.x_max)
            self.draw()

    def on_mouse_release(self, event):
        """Reset the pan start position when the left mouse button is released."""
        if event.button == 1:  # Left mouse button
            self.pan_start_x = None

    def on_mouse_scroll(self, event):
        """Zoom in or out at the mouse cursor position."""
        if event.xdata is None:
            return
        
        # Determine the zoom direction
        zoom_direction = -1 if event.button == 'up' else 1
        zoom_amount = zoom_direction * self.zoom_factor

        # Get current mouse position and axis limits
        mouse_x = event.xdata
        range_x = self.x_max - self.x_min
        
        # Calculate new limits
        new_range_x = range_x * (1 - zoom_amount)
        scale_factor = new_range_x / range_x

        new_x_min = mouse_x - (mouse_x - self.x_min) * scale_factor
        new_x_max = mouse_x + (self.x_max - mouse_x) * scale_factor

        # Ensure limits stay within the valid frequency range
        if new_x_min < 20:
            new_x_min = 20
        if new_x_max > 20000:
            new_x_max = 20000

        # Apply new limits
        self.x_min, self.x_max = new_x_min, new_x_max
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
