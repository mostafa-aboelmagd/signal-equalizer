import sys
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from classes import FileBrowser
import scipy.fftpack as fft
from UITEAM15 import Ui_MainWindow  # Import the Ui_MainWindow class

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setupUi(self) # Loads all components of the UI created using the designer
        self.magnitudes = [1] * 10
        self.sliders = [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.verticalSlider_5,
                        self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10]
        self.labels = [self.label_1_Hz, self.label_2_Hz, self.label_3_Hz, self.label_4_Hz, self.label_5_Hz,
                       self.label_6_Hz, self.label_7_Hz, self.label_8_Hz, self.label_9_Hz, self.label_10_Hz]
        self.defaultMode = True
        self.modeChanged = False
        self.setupUI() # Calls our custom method which links the UI elements
        self.retranslateUi(self)
        self.timer = QTimer()
        self.ranges = [
                       # uniform range frequency ranges
                       {"empty" : ()},
                       {
                        "Trumpet": (0, 500), 
                        "Xylophone" : (500, 1200),
                        "Brass": (1200, 6400),
                        "Celesta" : (4000, 13000)
                        },
                       {
                        "Dogs" : (0, 450),
                        "Wolves" : (450, 1100),
                        "Crow" : (1100, 3000),
                        "Bat" : (3000, 9000)
                        },
                       {
                        "Normal" : (0, 1000),
                        "Atrial Fibrillation" : (15, 20),
                        "Atrial Flutter" : (2, 8),
                        "Ventricular Fibrillation" : (0, 5)
                       }
                    ]
        self.samplingRates = [210, 27000, 19000, 2500]
        
        self.startDefault()
        self.connectSignals()
        self.plot_frequency_domain()

    def setupUI(self):
        self.file_browser = FileBrowser(self)
        self.inputViewBox = self.PlotWidget_inputSignal.getViewBox()
        self.outputViewBox = self.PlotWidget_outputSignal.getViewBox()
        self.inputViewBox.setXLink(self.outputViewBox)
        self.inputViewBox.setYLink(self.outputViewBox)
        self.pushButton.clicked.connect(self.file_browser.play_original_signal)
        self.pushButton_2.clicked.connect(self.file_browser.play_modified_signal)
        self.checkBox_showSpectrogram.stateChanged.connect(self.toggleSpectrogram)

    def startDefault(self):
        self.isPaused = False
        self.sampling_rate = 1000
        self.chunksize = 10
        self.curr_ptr = 0
        self.left_x_view = 0 # used in adjusting the view of the signal while running in cine mode
        self.right_x_view = self.left_x_view + 1
        self.time_values = np.linspace(0, 1, 1000)
        self.signal = self.generateSignal(magnitudes = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.modified_signal = self.signal
        if self.modeChanged:
            self.PlotWidget_inputSpectrogram.plotSpectrogram(None, 210)
            self.PlotWidget_outputSpectrogram.plotSpectrogram(None, 210)
            if self.checkBox_showSpectrogram.isChecked():
                self.PlotWidget_inputSpectrogram.showSpectrogram()
                self.PlotWidget_outputSpectrogram.showSpectrogram()
        self.timer.start(100)

    def connectSignals(self):      
        # Connect push buttons
        self.pushButton_playPause.clicked.connect(self.togglePlayPause)
        self.pushButton_zoomIn.clicked.connect(lambda: self.zoom(0.8))
        self.pushButton_zoomOut.clicked.connect(lambda: self.zoom(1.2))
        self.pushButton_reset.clicked.connect(lambda: self.stopAndReset(True))
        self.pushButton_stop.clicked.connect(lambda: self.stopAndReset(False))
        self.comboBox_modeSelection.currentIndexChanged.connect(self.changeMode)
        self.timer.timeout.connect(self.updateSignalView_timeDomain)
        self.pushButton_uploadButton.clicked.connect(self.uploadSignal)
        self.comboBox_frequencyScale.activated.connect(self.set_log_scale)
        self.speedSlider.valueChanged.connect(self.setSpeed)
   
        # Connect other UI elements
        for slider in self.sliders:
            slider.setMinimum(0)
            slider.setMaximum(10)
            slider.setValue(10)
            slider.setTickInterval(1)
            slider.valueChanged.connect(self.updateModifiedSignal)

    def plot_frequency_domain(self):
        self.PlotWidget_fourier.plot_frequency_domain(self.modified_signal, self.sampling_rate)
    
    def set_log_scale(self):
        if self.comboBox_frequencyScale.currentIndex() == 0:
            self.PlotWidget_fourier.log_scale = False
        else:
            self.PlotWidget_fourier.log_scale = True
        self.plot_frequency_domain()


    def uploadSignal(self):
        self.signal, self.sampling_rate = self.file_browser.browse_file("any")
        """if (self.comboBox_modeSelection.currentIndex() == 1 or 
            ((self.file_browser.fileName != "music") and (self.comboBox_modeSelection.currentIndex() == 1)) or 
            ((self.file_browser.fileName != "animals") and (self.comboBox_modeSelection.currentIndex() == 2))):
                self.signal = ""
                self.sampling_rate = 0
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                msg.setWindowTitle("Browsing Error")
                msg.setText("Choose A Different Mode To View This Signal")
                msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                msg.exec()  # Show the message box"""
        # Perform FFT
        self.freqs = fft.fftfreq(len(self.signal), 1 / self.sampling_rate) # returns an array of frequency values corresponding to each sample in the FFT result
        self.spectrum = fft.fft(self.signal) # returns an array containing frequency components, their magnitudes, and their phases
        self.plotSignal()

    def plotSignal(self):  
        self.left_x_view = 0 # used in adjusting the left x view of the signal while running in cine mode
        self.right_x_view  = self.left_x_view + 1  # adjusting the right x view
        self.duration = (1/self.sampling_rate) * len(self.signal)
        self.time_values = np.linspace(start = 0, stop = self.duration, num = len(self.signal))   # duration = Ts (time bet each 2 samples) * number of samples (len(self.signal))
        self.output_time_values = self.time_values
        self.isPaused = False
        self.PlotWidget_inputSignal.plotItem.setYRange(-1, 1)
        self.PlotWidget_inputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)    
        self.PlotWidget_inputSignal.plot(self.time_values, self.signal, pen = "r")
        self.updateModifiedSignal()  # starts the modified signal corresponding to the sliders values. (made it this way because when rewinding, sliders' values aren't necessiraly = 10, so op signal isn't necessiraly same as ip signal)
        self.timer.start(100)
        self.PlotWidget_inputSpectrogram.plotSpectrogram(self.signal, self.samplingRates[self.comboBox_modeSelection.currentIndex()])
        self.PlotWidget_outputSpectrogram.plotSpectrogram(self.modified_signal, self.samplingRates[self.comboBox_modeSelection.currentIndex()])
        if self.checkBox_showSpectrogram.isChecked():
            self.PlotWidget_inputSpectrogram.showSpectrogram()
            self.PlotWidget_outputSpectrogram.showSpectrogram()
        self.plot_frequency_domain()
        

    def updateSignalView_timeDomain(self):
        if len(self.signal) > 0 and self.isPaused == False:
            if self.defaultMode:
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


                if self.curr_ptr + self.chunksize < len(self.signal):
                    self.curr_ptr += self.chunksize
                    if self.time_values[self.curr_ptr] > self.left_x_view + 1:
                        self.left_x_view += 1

                else:
                    self.timer.stop()
                    self.isPaused = True 

            else:
                self.PlotWidget_inputSignal.plotItem.setYRange(-1, 1)
                self.PlotWidget_inputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)
                self.PlotWidget_outputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)
            
                self.left_x_view += 1/10   # incrementing the left view smoothly by matching the update time of the timer
                self.right_x_view = self.left_x_view + 1
                
                if self.right_x_view > self.duration:
                    self.timer.stop()
                    self.isPaused = True   

    
    def changeMode (self):
        self.modeChanged = True
        selected_index = self.comboBox_modeSelection.currentIndex()
        self.PlotWidget_inputSignal.clear()
        self.PlotWidget_outputSignal.clear()

        if selected_index == 0:
            self.defaultMode = True
            for i in range(len(self.sliders)):
                self.sliders[i].show()
                self.labels[i].show()
                sliderValue = (i + 1) * 10
                self.labels[i].setText(f"{sliderValue} Hz")
                self.sliders[i].setValue(10)
            self.startDefault()

        else:
            self.defaultMode = False
            self.PlotWidget_fourier.plot_frequency_domain([])
            self.PlotWidget_inputSpectrogram.hideSpectrogram()
            self.PlotWidget_outputSpectrogram.hideSpectrogram()
            self.isPaused = True
            self.left_x_view = 0 # used in adjusting the left x view of the signal while running in cine mode
            self.right_x_view  = self.left_x_view + 1  # adjusting the right x view
            self.shown_sliders_indices = [1, 3, 5, 7]

            for i in range(len(self.sliders)):
                idxShown = False
                for idx in self.shown_sliders_indices:
                    if i == idx:
                        idxShown = True
                
                if not idxShown:
                    self.sliders[i].hide()
                    self.labels[i].hide()
                        
            currDict = self.ranges[selected_index]   # the dictionary (corresponding to the chosen mode) containing ranges of frequencies for each slider from the list "ranges"
            loopCounter = 0
            for key in currDict:
                self.sliders[self.shown_sliders_indices[loopCounter]].setValue(10)  # initializing scale of each slider to be 1 (maximum)
                self.labels[self.shown_sliders_indices[loopCounter]].setText(key)   # adjusting label of each slider
                loopCounter += 1
            
            self.PlotWidget_inputSignal.clear()
            self.PlotWidget_outputSignal.clear()
            
            self.sliderFrequencyMap = {}  # contains each slider as a key, the starting and ending freqs (tuple) of its range of freqs as the value
            for i in range(len(self.shown_sliders_indices)):
                self.sliderFrequencyMap[self.sliders[self.shown_sliders_indices[i]]] = currDict[self.labels[self.shown_sliders_indices[i]].text()]   # output map:  {slider_1 : [0, 170] , slider_2: [180, 240], ...}

    def updateModifiedSignal(self):
        # Modify the frequency spectrum based on slider values
        if self.defaultMode:
            for i in range(0, 10):
                self.magnitudes[i] = self.sliders[i].value() / 10.0
                
            self.modified_signal = 0
            loopCounter = 0
            for i in range(10, 110, 10):
                self.modified_signal += self.magnitudes[loopCounter] * np.sin(2* np.pi * i * self.time_values)
                loopCounter += 1

            # Update the output signal in real-time
            self.PlotWidget_outputSignal.clear()  # Clear the previous plot
            self.PlotWidget_outputSignal.plot(self.time_values[ : self.curr_ptr + self.chunksize], self.modified_signal[ : self.curr_ptr + self.chunksize], pen='b')

            # If we're playing, don't stop the timer
            if not self.isPaused:
                self.togglePlayPause()

            self.PlotWidget_outputSpectrogram.update(None, self.magnitudes)
            self.plot_frequency_domain()

        else:
            modified_spectrum = self.spectrum.copy()

            loopCounter = 0
            for key in self.ranges[self.comboBox_modeSelection.currentIndex()]:
                low, high = self.ranges[self.comboBox_modeSelection.currentIndex()][key]
                slider_value = self.sliders[self.shown_sliders_indices[loopCounter]].value() / 10.0
                loopCounter += 1

                # Apply gain to the selected frequency range
                mask = (np.abs(self.freqs) >= low) & (np.abs(self.freqs) <= high)
                modified_spectrum[mask] *= slider_value
                
            # Perform inverse FFT to get the modified time-domain signal
            self.modified_signal = np.real(fft.ifft(modified_spectrum))

            self.file_browser.modified_signal = self.modified_signal
            self.output_time_values = np.linspace(start = 0, stop = self.duration, num = len(self.modified_signal))
            self.PlotWidget_outputSignal.clear()
            self.PlotWidget_outputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)
            self.PlotWidget_outputSignal.plot(self.output_time_values, self.modified_signal, pen = "b")
            self.PlotWidget_outputSpectrogram.update(self.modified_signal, [-1])
        
        
    """def computeFourierTransform(self):
        self.freq_components = np.fft.fft(self.signal)    # returns 1d np array containing freq all freq components (mag and phase, not the freq itself) of sinusoidals sharing in the signal.
        self.frequencies = np.fft.fftfreq(len(self.signal), 1/self.sampling_rate)  # the frequencies themselves that are sharing in the signal, not their components. Parameters are num of pts in the signal and time spacing between each 2 pts.
        self.magnitudes = np.abs(self.freq_components)     # obtaining magnitudes corresponding to each freq component.
        self.phase_angles = np.angle(self.freq_components)   # obtaining phase angles corresponding to each freq component
        
        #print(f"max frequency: {self.frequencies[len(self.frequencies) // 2]}") # for debugging
        
        # looping on all sliders:
        for slider in self.sliders:

            # getting new freq components corresponding to the change occurred to mags of each slider
            if self.sliders.index(slider) in self.shown_sliders_indices:  # if the idx of the current slider is in the shown sliders indices (the slider being checked is in use)
                min_slider_freq = self.sliderFrequencyMap[slider][0]
                max_slider_freq = self.sliderFrequencyMap[slider][1]  # bound frequencies of the range that this slider holds
                slider_freq_indices = np.where((self.frequencies >= min_slider_freq) & (self.frequencies <= max_slider_freq))[0]  # indices of frequencies this range in the "frequencies" array
                #print(f" range indices: {slider_freq_indices}")  # for debugging
                self.magnitudes[slider_freq_indices] *= (slider.value()/10) # new magnitudes in this range corresponding to the slider's value     
                self.freq_components[slider_freq_indices] = self.magnitudes[slider_freq_indices] * np.exp(1j * self.phase_angles[slider_freq_indices]) # updating frequency components array in this range
        
        #print(f"length of frequencies array: {len(self.frequencies)}")  # for debugging
        #print(f"frequencies corrsponding to last slider: {self.frequencies[slider_freq_indices]}")
        #print(f"magnitudes corresponding to last slider: {new_slider_magnitudes}")
        
        modified_signal = self.invFourierTransform()
        return modified_signal


    def invFourierTransform(self):
        modified_signal = np.fft.ifft(self.freq_components).real
        return modified_signal"""

    def togglePlayPause(self):
        if self.isPaused == True:
            self.isPaused = False
            self.timer.start(100)
        else:
            self.isPaused = True
            self.timer.stop()
            

    def setSpeed(self, speed):
        self.timer.setInterval(int(100 / speed))

    def stopAndReset(self, reset):
        self.timer.stop()
        self.isPaused = True
        if reset:
            self.plotSignal()     

    def zoom(self, factor):
        self.PlotWidget_inputSignal.plotItem.getViewBox().scaleBy((factor, 1))
        # self.PlotWidget_outputSignal.plotItem.getViewBox().scaleBy((factor, 1))
       
    def generateSignal(self, magnitudes):
        signal = 0
        loopCounter = 0
        for i in range(10, 110, 10):
            signal += magnitudes[loopCounter] * np.sin(2 * np.pi * i * self.time_values)
            loopCounter += 1
        return signal
    
    def toggleSpectrogram(self):
        if self.checkBox_showSpectrogram.isChecked():
            self.PlotWidget_inputSpectrogram.showSpectrogram()
            self.PlotWidget_outputSpectrogram.showSpectrogram()
        else:
            self.PlotWidget_inputSpectrogram.hideSpectrogram()
            self.PlotWidget_outputSpectrogram.hideSpectrogram()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
