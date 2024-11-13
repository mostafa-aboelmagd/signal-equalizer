import sys
import numpy as np
import pandas as pd
import soundfile as sf
import scipy
from scipy import signal
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as pyo
import copy
 
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QMessageBox, QApplication, QVBoxLayout, QWidget , QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from UITEAM15 import Ui_MainWindow  # Import the Ui_MainWindow class

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setupUi(self)
        self.magnitudes = [1] * 10
        self.sliders = [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.verticalSlider_5,
                        self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10]
        self.setupUI()
        self.connectSignals()
        self.sample_rate = 44100  # Default sample rate
        self.signal = np.zeros(44100)  # Default empty signal (1 second of silence)

    def setupUI(self):
        """Setup UI elements and initial configurations."""
        # Link input and output view boxes
        self.inputViewBox = self.PlotWidget_inputSignal.getViewBox()
        self.outputViewBox = self.PlotWidget_outputSignal.getViewBox()
        self.inputViewBox.setXLink(self.outputViewBox)
        self.inputViewBox.setYLink(self.outputViewBox)

    def connectSignals(self):
        """Connect UI signals to their respective slots."""
        # Connect comboBox actions
        #self.pushButton_uploadButton.clicked.connect(self.uploadAndPlotSignal)
      
        # Connect push buttons
        #self.pushButton_playPause.clicked.connect(self.togglePlayPause)
        #self.pushButton_zoomIn.clicked.connect(lambda: self.zoom(0.5))
        #self.pushButton_zoomOut.clicked.connect(lambda: self.zoom(2))
        #self.pushButton_reset.clicked.connect(lambda: self.stopAndReset(True))
        #self.pushButton_stop.clicked.connect(lambda: self.stopAndReset(False))
   
        # Connect other UI elements
        self.checkBox_showSpectrogram.stateChanged.connect(self.showAndHideSpectrogram)
        for slider in self.sliders:
            slider.setMinimum(0)
            slider.setMaximum(10)
            slider.setValue(10)
            slider.setTickInterval(1)
            slider.valueChanged.connect(self.updateSpectrogram)

    def plot_frequency_domain(self):
        self.PlotWidget_fourier.plot_frequency_domain(self.signal, self.sample_rate)

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

        #self.comboBox_frequencyScale.activated.connect(self.setFrequencyScale)
    
    def showAndHideSpectrogram(self):
        if self.checkBox_showSpectrogram.isChecked():
            self.PlotWidget_inputSpectrogram.show()
            self.PlotWidget_outputSpectrogram.show()
        else:
            self.PlotWidget_inputSpectrogram.hide()
            self.PlotWidget_outputSpectrogram.hide()
    
    def updateSpectrogram(self):
        for i in range(0, 10):
            self.magnitudes[i] = self.sliders[i].value() / 10.0
        
        self.PlotWidget_outputSpectrogram.update(self.magnitudes)
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
