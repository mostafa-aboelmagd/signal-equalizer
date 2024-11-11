import os
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
from PyQt5.QtWidgets import QMessageBox, QApplication, QVBoxLayout, QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from classes import FileBrowser

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        uic.loadUi('UITeam15.ui', self)
        self.setupUI()
        self.connectSignals()

    def setupUI(self):
        """Setup UI elements and initial configurations."""
        # Link input and output view boxes
        self.inputViewBox = self.PlotWidget_inputSignal.getViewBox()
        self.outputViewBox = self.PlotWidget_outputSignal.getViewBox()
        self.inputViewBox.setXLink(self.outputViewBox)
        self.inputViewBox.setYLink(self.outputViewBox)
        self.PlotWidget_fourier.setLabel('left', 'Magnitude')
        self.PlotWidget_fourier.setLabel('bottom', 'Frequency')

    def connectSignals(self):
        """Connect UI signals to their respective slots."""
        # Connect menu actions
        self.actionOpen.triggered.connect(self.uploadAndPlotSignal)
        self.actionClose.triggered.connect(self.closeApp)

        mode_actions = {
            self.actionUniform: "uniform",
            self.actionMusical: "musical instruments",
            self.actionAnimal_Sounds: "animal sounds",
            self.actionECG_Abnormalities: "ECG abn",
        }

        for action, mode in mode_actions.items():
            action.triggered.connect(lambda _, m=mode: self.setMode(m))

        # Connect push buttons
        self.pushButton_playPause.clicked.connect(self.togglePlayPause)
        self.pushButton_zoomIn.clicked.connect(lambda: self.zoom(0.5))
        self.pushButton_zoomOut.clicked.connect(lambda: self.zoom(2))
        self.pushButton_reset.clicked.connect(lambda: self.stopAndReset(True))
        self.pushButton_stop.clicked.connect(lambda: self.stopAndReset(False))
        self.pushButton_applySmoothing.clicked.connect(self.setWindowParameters)

        # Connect other UI elements
        self.checkBox_showSpectrogram.stateChanged.connect(self.showAndHideSpectrogram)
        self.comboBox_smoothingWindows.activated.connect(self.setSmoothingWindow)

    def closeApp(self):
        """Close the application."""
        QApplication.instance().quit()

    def setMode(self, mode):
        """Set the mode of the application."""
        self.clearAll()
        self.mode = mode
        self.isAudio, self.numberOfSliders, self.fMin, self.fMax, edit_labels = FileBrowser.set_mode(self.fileBrowser, mode)
        if edit_labels:
            for i in range(self.numberOfSliders):
                label = getattr(self, f"label_{i + 1}_Hz")
                label.setText(f"{str(self.fMax[i])} Hz")

    def uploadAndPlotSignal(self):
        """Upload and plot the signal."""
        pass

    def plotSignal_timeDomain(self, audio, audioSamplingRate, signal, widget):
        """Plot the signal in the time domain."""
        pass

    def plotSpectrogram(self, fig, canvas, audio, audioSamplingRate, signal):
        """Plot the spectrogram of the signal."""
        pass

    def plotFrequencySpectrum(self):
        """Plot the frequency spectrum of the signal."""
        pass

    def computeFourierTransform(self):
        """Compute the Fourier transform of the signal."""
        pass

    def invFourierTransform(self, magnitude, phase):
        """Compute the inverse Fourier transform."""
        pass

    def setSmoothingWindow(self):
        """Set the smoothing window."""
        pass

    def setWindowParameters(self):
        """Set the parameters for the smoothing window."""
        pass

    def getMappedSliderValue(self, slider_value):
        """Get the mapped value of the slider."""
        pass

    def generateWindow(self, sliderNumber, Value):
        """Generate the window for smoothing."""
        pass

    def applySmoothingWindow(self, gainList, targetBand):
        """Apply the smoothing window."""
        pass

    def togglePlayPause(self):
        """Toggle play/pause of the signal."""
        pass

    def setSpeed(self, speed):
        """Set the playback speed."""
        pass

    def stopAndReset(self, reset):
        """Stop and reset the signal."""
        pass

    def zoom(self, factor):
        """Zoom in or out on the signal."""
        pass

    def showAndHideSpectrogram(self, state):
        """Show or hide the spectrogram."""
        pass

    def get_min_max_for_widget(self, widget, data_type):
        """Get the min and max values for the widget."""
        pass

    def clearAll(self):
        """Clear all data and reset the UI."""
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
