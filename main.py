import sys
from PyQt5 import QtWidgets
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
