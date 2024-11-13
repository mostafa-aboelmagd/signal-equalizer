import sys
import numpy as np
import librosa
 
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from classes import FileBrowser
from PyQt5 import QtWidgets
from UITEAM15 import Ui_MainWindow  # Import the Ui_MainWindow class
import classes

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setupUi(self)
        self.magnitudes = [1] * 10
        self.sliders = [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.verticalSlider_5,
                        self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10]
        self.setupUI()
        self.retranslateUi(self)
        self.timer = QTimer()
        self.isPaused = False
        self.sampling_rate = 0
        self.chunksize = 10
        self.curr_ptr = 0
        self.left_x_view = 0 # used in adjusting the view of the signal while running in cine mode
        self.startDefault()
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
    
    def startDefault(self):
        self.isPaused = False
        self.sampling_rate = 0
        self.chunksize = 10
        self.curr_ptr = 0
        self.left_x_view = 0 # used in adjusting the view of the signal while running in cine mode
        if self.checkBox_showSpectrogram.isChecked():
            self.PlotWidget_inputSpectrogram.showSpectrogram()
            self.PlotWidget_outputSpectrogram.showSpectrogram()
        self.time_values = np.linspace(0, 1, 1000)
        self.signal = self.generateSignal(magnitudes = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.modified_signal = self.signal
        self.timer.start(100)

    def connectSignals(self):
        """Connect UI signals to their respective slots."""
        # Connect comboBox actions
        #self.pushButton_uploadButton.clicked.connect(self.uploadAndPlotSignal)
      
        # Connect push buttons
        self.pushButton_playPause.clicked.connect(self.togglePlayPause)
        self.pushButton_zoomIn.clicked.connect(lambda: self.zoom(0.5))
        self.pushButton_zoomOut.clicked.connect(lambda: self.zoom(2))
        self.pushButton_reset.clicked.connect(lambda: self.stopAndReset(True))
        self.pushButton_stop.clicked.connect(lambda: self.stopAndReset(False))
        self.comboBox_modeSelection.currentIndexChanged.connect(self.changeMode)
        self.timer.timeout.connect(self.plotSignal_timeDomain)
   
        # Connect other UI elements
        self.checkBox_showSpectrogram.stateChanged.connect(self.showAndHideSpectrogram)
        for slider in self.sliders:
            slider.setMinimum(0)
            slider.setMaximum(10)
            slider.setValue(10)
            slider.setTickInterval(1)
            slider.valueChanged.connect(self.updateOutput)
        #self.comboBox_frequencyScale.activated.connect(self.setFrequencyScale)

    def setMode(self, mode):
        """Set the mode of the application."""
        pass

    def uploadAndPlotSignal(self):
        """Upload and plot the signal."""
        file_browser = FileBrowser()
        self.signal, self.sampling_rate = file_browser.browse_file(mode= 'music')
        #self.plotSignal_timeDomain(self.sampling_rate, self.signal)
        self.chunksize = 1000
        self.curr_ptr = 0
        self.left_x_view = 0 # used in adjusting the view of the signal while running in cine mode
        self.time_values = np.linspace(0, 10, len(self.signal))
        #self.plotSignal_timeDomain()
        self.timer.start(100)
        

    def plotSignal_timeDomain(self):
        """Plot the signal in the time domain."""
        if len(self.signal) > 0 and self.isPaused == False:
            # taking chunks from the signal and the corresponding time values
            self.segment_y_ip = self.signal[self.curr_ptr : self.curr_ptr + self.chunksize]   # from index "curr_ptr" to index "curr_ptr + chunksize"
            self.segment_y_op = self.modified_signal[self.curr_ptr : self.curr_ptr + self.chunksize]
            self.segment_x = self.time_values[ self.curr_ptr : self.curr_ptr + self.chunksize]  # same in time values stored for the signal
            
            self.PlotWidget_inputSignal.plotItem.setYRange(-1, 1)
            self.PlotWidget_inputSignal.plotItem.setXRange(self.left_x_view, self.left_x_view + 1)
            self.PlotWidget_outputSignal.plotItem.setYRange(-1, 1)
            self.PlotWidget_outputSignal.plotItem.setXRange(self.left_x_view, self.left_x_view + 1)
            self.PlotWidget_inputSignal.plot(self.segment_x, self.segment_y_ip, pen = 'r')
            self.PlotWidget_outputSignal.plot(self.segment_x, self.segment_y_op, pen = 'b')

            
            if self.curr_ptr + self.chunksize <= len(self.signal):
                self.curr_ptr += self.chunksize
                if self.time_values[self.curr_ptr + self.chunksize] > self.left_x_view + 1:
                    self.left_x_view += 1
                
            else:
                self.timer.stop()
                self.isPaused = True
           
           
    def plotSpectrogram(self, fig, canvas, audio, audioSamplingRate, signal):
        """Plot the spectrogram of the signal."""
        pass

    def plotFrequencySpectrum(self):
        """Plot the frequency spectrum of the signal."""
        pass

   

    def computeFourierTransform(self):
        """Compute the Fourier transform of the signal."""
        self.fft_data = librosa.stft(self.signal)
        self.magnitude, self.phase = librosa.magphase(self.fft_data)
        

    def invFourierTransform(self, magnitude, phase):
        """Compute the inverse Fourier transform."""
        self.modified_fft_data = self.magnitude * self.phase
        self.modified_signal = librosa.istft(self.modified_fft_data)
        

    def changeMode (self):
        selected_index = self.comboBox_modeSelection.currentIndex()
        if selected_index == 0:
            self.startDefault()
            self.verticalSlider_1.show()
            self.verticalSlider_2.show()
            self.verticalSlider_3.show()
            self.verticalSlider_4.show()
            self.verticalSlider_5.show()
            self.verticalSlider_6.show()
            self.verticalSlider_7.show()
            self.verticalSlider_8.show()
            self.verticalSlider_9.show()
            self.verticalSlider_10.show()
            
        else:
            self.PlotWidget_outputSignal.clear()
            self.PlotWidget_inputSignal.clear()
            self.PlotWidget_inputSpectrogram.hideSpectrogram()
            self.PlotWidget_outputSpectrogram.hideSpectrogram()
            self.isPaused = True

            self.verticalSlider_1.hide()
            self.verticalSlider_3.hide()
            self.verticalSlider_5.hide()
            self.verticalSlider_7.hide()
            self.verticalSlider_9.hide()
            self.verticalSlider_10.hide()
       
    
    
    def getMappedSliderValue(self, slider_value):
        """Get the mapped value of the slider."""
        selected_index = self.comboBox_modeSelection.currentIndex()
        if selected_index == 0:
            pass
        
        else:
            pass


    def togglePlayPause(self):
        """Toggle play/pause of the signal."""
        if self.isPaused == True:
            self.isPaused = False
            self.timer.start(100)
        else:
            self.isPaused = True
            self.timer.stop()
            

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

   
    def clearAll(self):
        """Clear all data and reset the UI."""
        pass

    def generateSignal(self, magnitudes):
        
        signal = 0
        loopCounter = 0
        for i in range(10, 110, 10):
            signal+= magnitudes[loopCounter] * np.sin(2* np.pi * i * self.time_values)
            loopCounter +=1
        return signal
    
    def showAndHideSpectrogram(self):
        if self.checkBox_showSpectrogram.isChecked():
            self.PlotWidget_inputSpectrogram.showSpectrogram()
            self.PlotWidget_outputSpectrogram.showSpectrogram()
        else:
            self.PlotWidget_inputSpectrogram.hideSpectrogram()
            self.PlotWidget_outputSpectrogram.hideSpectrogram()
    
    def updateOutput(self):
        for i in range(0, 10):
            self.magnitudes[i] = self.sliders[i].value() / 10.0
                
        self.modified_signal = 0
        loopCounter = 0
        for i in range(10, 110, 10):
            self.modified_signal += self.magnitudes[loopCounter] * np.sin(2* np.pi * i * self.time_values)
            loopCounter +=1
        
        # Update the output signal in real-time
        self.PlotWidget_outputSignal.clear()  # Clear the previous plot
        self.PlotWidget_outputSignal.plot(self.time_values[ : self.curr_ptr + self.chunksize], self.modified_signal[ : self.curr_ptr + self.chunksize], pen='b')

        # If we're playing, don't stop the timer
        if not self.isPaused:
            self.togglePlayPause()

        self.PlotWidget_outputSpectrogram.update(self.magnitudes)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
