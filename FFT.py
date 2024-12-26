import sys
import numpy as np
import soundfile as sf
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt5.QtCore import QTimer
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
        self.log_scale =  False  # Linear scale by default
        self.pan_start_x = None  # For panning
        self.zoom_factor = 0.1  # 10% zoom
        self.max_freq = 0
        
        # Enable mouse tracking and set up Matplotlib event handlers
        self.mpl_connect("button_press_event", self.on_mouse_press)
        self.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.mpl_connect("button_release_event", self.on_mouse_release)
        self.mpl_connect("scroll_event", self.on_mouse_scroll)

        # Timer to delay updates for smoother transitions
        """self.updateTimer = QTimer(self)
        self.updateTimer.setSingleShot(True)  # Make sure it only fires once even if it was fired multiple times before ending
        self.updateTimer.timeout.connect(lambda : self.plot_frequency_domain(self.modifiedSignal))"""
    
    # Hide the canvas from within the FFTPlotCanvas class
    def hideCanvas(self):
        self.setVisible(False)  # Hides the canvas

    # Show the canvas from within the FFTPlotCanvas class
    def showCanvas(self):
        self.setVisible(True)  # Shows the canvas
    
    #def update(self):
    #    self.updateTimer.start(150)  # 150ms delay before redrawing

    def plot_frequency_domain(self, signal, sample_rate = 44100):
        if signal is None or len(signal) == 0:
            self.ax.clear()
            return
        self.ax.clear()
        # Compute FFT
        N = len(signal)
        freq_components = np.fft.fft(signal)
        freq_magnitude = np.abs(freq_components[:N // 2])
        freq_magnitude_db = 20 * np.log10(freq_magnitude + 1e-12)
        freq_bins = np.fft.fftfreq(N, d=1 / sample_rate)[:N // 2]
        # check the magnitude of the frequency bins and do not plot the ones that are too small
        x_lim = 10
        for mag in reversed(freq_magnitude_db):
            if mag > x_lim:
                break
            else:
                freq_bins = freq_bins[:-1]
                freq_magnitude = freq_magnitude[:-1]
                freq_magnitude_db = freq_magnitude_db[:-1]
        
        # set the x-axis limits
        self.max_freq = max(freq_bins)

        # Plot settings
        if self.log_scale:
            self.ax.set_xscale('log')
            self.ax.set_ylim(bottom=120, top=-20) 
            self.ax.plot(freq_bins, freq_magnitude_db, 'r')
        else:
            self.ax.set_xscale('linear')
            self.ax.plot(freq_bins, freq_magnitude, 'r')
        
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Magnitude")
        self.ax.grid(True)
        if self.x_max == None:
            self.ax.set_xlim(0, self.max_freq)
            self.x_min, self.x_max = 0 , self.max_freq
        elif self.log_scale and self.x_min < 1:
            self.ax.set_xlim(1, self.x_max)
        else:
            self.ax.set_xlim(self.x_min,self.x_max)
        self.draw()

    def on_mouse_press(self, event):
        """Capture the initial x-coordinate when the left mouse button is pressed."""
        if event.button == 1 and event.xdata is not None:  # Left mouse button
            self.pan_start_x = event.xdata

    def on_mouse_move(self, event):
        """Handle mouse drag events for panning left and right."""
        if not self.max_freq:
            return
        if self.pan_start_x is not None and event.xdata is not None:
            # Calculate the delta to move the plot
            if self.log_scale:
                delta_x = (self.pan_start_x - event.xdata)*0.5

            else: 
                delta_x = (self.pan_start_x - event.xdata)
            self.pan_start_x = event.xdata

            # Adjust the x-axis limits for panning

            # Ensure limits stay within the valid frequency range
            if self.x_min + delta_x > 0 and self.x_max + delta_x <= self.max_freq:
                self.x_min = self.x_min + delta_x
                self.x_max = self.x_max + delta_x

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
       
        if self.log_scale and new_x_min < 1:
            new_x_min = 1
        elif new_x_min < 0:
            new_x_min = 0
        if new_x_max > self.max_freq:
            new_x_max = self.max_freq

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