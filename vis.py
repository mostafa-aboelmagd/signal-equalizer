import sys
import numpy as np
from scipy import signal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QWidget, QLabel
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from pydub import AudioSegment
import sounddevice as sd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider

class AudioPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Player with Input and Output Visualization")
        self.setGeometry(200, 200, 1000, 900)

        # Main widget and layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        # Input Signal Plot
        self.input_plot_label = QLabel("Input Signal:")
        self.layout.addWidget(self.input_plot_label)

        self.input_plot_widget = pg.PlotWidget(title="Input Signal")
        self.input_plot_widget.setLabel('left', 'Amplitude')
        self.input_plot_widget.setLabel('bottom', 'Time', 's')
        self.input_plot_widget.setLimits(xMin=0)
        self.layout.addWidget(self.input_plot_widget)

        # Input controls layout
        self.input_controls = QHBoxLayout()
        self.layout.addLayout(self.input_controls)

        # Input control buttons
        self.load_button = QPushButton("Load Audio File")
        self.load_button.clicked.connect(self.load_audio)
        self.input_controls.addWidget(self.load_button)

        self.play_button = QPushButton("Play Input")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.play_audio)
        self.input_controls.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause Input")
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_audio)
        self.input_controls.addWidget(self.pause_button)

        self.rewind_button = QPushButton("Rewind Input")
        self.rewind_button.setEnabled(False)
        self.rewind_button.clicked.connect(self.rewind_audio)
        self.input_controls.addWidget(self.rewind_button)

        self.wiener_button = QPushButton("Apply Wiener Filter")
        self.wiener_button.setEnabled(False)
        self.wiener_button.clicked.connect(self.enable_noise_selection)
        self.input_controls.addWidget(self.wiener_button)

        # Output Signal Plot
        self.output_plot_label = QLabel("Output Signal:")
        self.layout.addWidget(self.output_plot_label)

        self.output_plot_widget = pg.PlotWidget(title="Output Signal")
        self.output_plot_widget.setLabel('left', 'Amplitude')
        self.output_plot_widget.setLabel('bottom', 'Time', 's')
        self.output_plot_widget.setLimits(xMin=0)
        self.layout.addWidget(self.output_plot_widget)

        # Output controls layout
        self.output_controls = QHBoxLayout()
        self.layout.addLayout(self.output_controls)

        # Output control buttons
        self.play_output_button = QPushButton("Play Output")
        self.play_output_button.setEnabled(False)
        self.play_output_button.clicked.connect(self.play_output_audio)
        self.output_controls.addWidget(self.play_output_button)

        self.pause_output_button = QPushButton("Pause Output")
        self.pause_output_button.setEnabled(False)
        self.pause_output_button.clicked.connect(self.pause_output_audio)
        self.output_controls.addWidget(self.pause_output_button)

        self.rewind_output_button = QPushButton("Rewind Output")
        self.rewind_output_button.setEnabled(False)
        self.rewind_output_button.clicked.connect(self.rewind_output_audio)
        self.output_controls.addWidget(self.rewind_output_button)

        # Add after your existing controls
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(100)
        self.alpha_slider.setValue(12)  # Default alpha = 1.2
        self.alpha_slider.setEnabled(False)
        self.alpha_label = QLabel("Alpha: 1.2")
        
        # Add slider to layout
        self.alpha_control = QHBoxLayout()
        self.alpha_control.addWidget(QLabel("Filter Strength:"))
        self.alpha_control.addWidget(self.alpha_slider)
        self.alpha_control.addWidget(self.alpha_label)
        self.layout.addLayout(self.alpha_control)
        
        # Connect slider
        self.alpha_slider.valueChanged.connect(self.update_alpha)

        # Variables for audio and playback
        self.audio_data = None
        self.filtered_audio = None
        self.sampling_rate = None
        self.timer = None
        self.output_timer = None
        self.current_index = 0
        self.output_current_index = 0
        self.chunk_size = None
        self.is_playing = False
        self.is_output_playing = False
        self.full_signal_plot = None
        self.output_signal_plot = None
        self.current_position_marker = None
        self.output_position_marker = None
        self.region = None
        self.times = None

    def load_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3 *.wav)")
        if file_path:
            self.process_audio(file_path)

    def process_audio(self, file_path):
        # Load and process audio file as before
        if file_path.endswith(".mp3"):
            audio = AudioSegment.from_mp3(file_path)
        elif file_path.endswith(".wav"):
            audio = AudioSegment.from_wav(file_path)
        else:
            return

        self.sampling_rate = audio.frame_rate
        samples = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)

        self.audio_data = samples / np.max(np.abs(samples))
        self.chunk_size = self.sampling_rate // 10
        self.current_index = 0
        self.output_current_index = 0

        # Plot the input waveform
        self.times = np.linspace(0, len(self.audio_data) / self.sampling_rate, num=len(self.audio_data))
        self.input_plot_widget.clear()
        self.full_signal_plot = self.input_plot_widget.plot(self.times, self.audio_data, pen='b')

        # Add position marker for input signal
        if self.current_position_marker is not None:
            self.input_plot_widget.removeItem(self.current_position_marker)
        self.current_position_marker = self.input_plot_widget.addLine(x=0, pen=pg.mkPen('r', width=2))

        # Clear output plot
        self.output_plot_widget.clear()
        if self.output_position_marker is not None:
            self.output_plot_widget.removeItem(self.output_position_marker)

        # Enable buttons
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.rewind_button.setEnabled(True)
        self.wiener_button.setEnabled(True)
        
        # Disable output playback buttons until filtering is done
        self.play_output_button.setEnabled(False)
        self.pause_output_button.setEnabled(False)
        self.rewind_output_button.setEnabled(False)

    def enable_noise_selection(self):
        if self.region is not None:
            self.input_plot_widget.removeItem(self.region)
        self.region = pg.LinearRegionItem()
        self.input_plot_widget.addItem(self.region)
        self.region.sigRegionChangeFinished.connect(self.apply_wiener_filter)
        self.alpha_slider.setEnabled(True)

    def update_alpha(self):
        alpha_value = self.alpha_slider.value() / 10
        self.alpha_label.setText(f"Alpha: {alpha_value:.1f}")
        if hasattr(self, 'region'):
            self.apply_wiener_filter()

    def apply_wiener_filter(self):
        if self.region is not None and self.audio_data is not None:
            try:
                # Get alpha from slider
                alpha = self.alpha_slider.value() / 10
                
                # Rest of your existing filter code, replacing the hardcoded alpha
                region_min, region_max = self.region.getRegion()
                sample_min = int(region_min * self.sampling_rate)
                sample_max = int(region_max * self.sampling_rate)
                noise = self.audio_data[sample_min:sample_max]
                
                # Parameters
                nfft = 2048
                hop = nfft // 4
                window = np.hanning(nfft)
                
                # Estimate noise spectrum
                noise_spectra = []
                for i in range(0, len(noise) - nfft, hop):
                    segment = noise[i:i + nfft] * window
                    noise_spectra.append(np.abs(np.fft.fft(segment))**2)
                noise_psd = np.mean(noise_spectra, axis=0)
                
                self.filtered_audio = np.zeros(len(self.audio_data))
                
                for i in range(0, len(self.audio_data) - nfft, hop):
                    segment = self.audio_data[i:i + nfft] * window
                    spectrum = np.fft.fft(segment)
                    power = np.abs(spectrum)**2
                    
                    eps = 1e-6
                    snr = np.maximum(power / (noise_psd + eps) - 1, 0)
                    H = snr / (snr + alpha)
                    
                    freq_smooth = np.linspace(0.5, 1.0, len(H)//2)
                    H[:len(H)//2] *= freq_smooth
                    H[len(H)//2:] *= freq_smooth[::-1]
                    
                    filtered = np.fft.ifft(spectrum * H)
                    self.filtered_audio[i:i + nfft] += np.real(filtered) * window
                
                norm_factor = np.sum(np.hanning(nfft)**2)
                self.filtered_audio /= norm_factor
                self.filtered_audio /= np.max(np.abs(self.filtered_audio))
                
                self.output_plot_widget.clear()
                self.output_signal_plot = self.output_plot_widget.plot(
                    self.times[:len(self.filtered_audio)], 
                    self.filtered_audio, 
                    pen='g'
                )
                
                self.output_position_marker = self.output_plot_widget.addLine(x=0, pen=pg.mkPen('r', width=2))
                self.play_output_button.setEnabled(True)
                self.pause_output_button.setEnabled(True)
                self.rewind_output_button.setEnabled(True)
                
            except Exception as e:
                print(f"Error applying Wiener filter: {str(e)}")

    def play_audio(self):
        if self.audio_data is not None and not self.is_playing:
            self.is_playing = True
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_plot)
            self.timer.start(100)

            start_sample = self.current_index
            sd.play(self.audio_data[start_sample:], samplerate=self.sampling_rate)

    def play_output_audio(self):
        if self.filtered_audio is not None and not self.is_output_playing:
            self.is_output_playing = True
            self.output_timer = QTimer()
            self.output_timer.timeout.connect(self.update_output_plot)
            self.output_timer.start(100)

            start_sample = self.output_current_index
            sd.play(self.filtered_audio[start_sample:], samplerate=self.sampling_rate)

    def pause_audio(self):
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
            sd.stop()

    def pause_output_audio(self):
        if self.is_output_playing:
            self.is_output_playing = False
            self.output_timer.stop()
            sd.stop()

    def rewind_audio(self):
        if self.audio_data is not None:
            self.pause_audio()
            self.current_index = 0
            if self.is_playing:
                self.play_audio()
            else:
                self.update_plot()

    def rewind_output_audio(self):
        if self.filtered_audio is not None:
            self.pause_output_audio()
            self.output_current_index = 0
            if self.is_output_playing:
                self.play_output_audio()
            else:
                self.update_output_plot()

    def update_plot(self):
        if self.audio_data is not None:
            start = self.current_index
            end = start + self.chunk_size

            if end > len(self.audio_data):
                end = len(self.audio_data)
                self.pause_audio()
                self.current_index = 0

            current_time = start / self.sampling_rate
            self.current_position_marker.setValue(current_time)
            self.current_index += self.chunk_size

    def update_output_plot(self):
        if self.filtered_audio is not None:
            start = self.output_current_index
            end = start + self.chunk_size

            if end > len(self.filtered_audio):
                end = len(self.filtered_audio)
                self.pause_output_audio()
                self.output_current_index = 0

            current_time = start / self.sampling_rate
            self.output_position_marker.setValue(current_time)
            self.output_current_index += self.chunk_size

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioPlayer()
    window.show()
    sys.exit(app.exec_())





