import sys
import numpy as np
import librosa
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from classes import FileBrowser
from PyQt5 import QtWidgets
from UITEAM15 import Ui_MainWindow  # Import the Ui_MainWindow class

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setupUi(self)
        self.magnitudes = [1] * 10
        self.sliders = [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.verticalSlider_5,
                        self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10]
        self.labels = [self.label_1_Hz, self.label_2_Hz, self.label_3_Hz, self.label_4_Hz, self.label_5_Hz, self.label_6_Hz,
                       self.label_7_Hz, self.label_8_Hz, self.label_9_Hz, self.label_10_Hz]
        self.setupUI()
        self.retranslateUi(self)
        self.timer = QTimer()
        self.ranges = [
                       # uniform range frequency ranges
                       [],
                       {"Guitar": [0, 170], 
                         "Flute" : [170, 250],
                         "Harmonica": [250, 400],
                         "Xylophone" : [400, 1000]},
                       {"Dogs" : [0, 450],
                        "Wolves" : [450, 1100],
                        "Crow" : [1100, 3000],
                        "Bat" : [3000, 9000]},
                       {"Tachycardia & Couplets" : [0, 6.5],
                        "Couplets Only" : [0, 5],
                        "Tachycardia Only" : [0, 8],
                        "Normal" : [0, 9]
                       }
                       ]

        self.startDefault()
        self.connectSignals()
        self.plot_frequency_domain()


    def setupUI(self):
        """Setup UI elements and initial configurations."""
        # Link input and output view boxes
        self.inputViewBox = self.PlotWidget_inputSignal.getViewBox()
        self.outputViewBox = self.PlotWidget_outputSignal.getViewBox()
        self.inputViewBox.setXLink(self.outputViewBox)
        self.inputViewBox.setYLink(self.outputViewBox)
    
    def startDefault(self):
        self.isPaused = False
        self.sampling_rate = 1000
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
        self.checkBox_showSpectrogram.stateChanged.connect(self.showAndHideSpectrogram)
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
        """Upload and plot the signal."""
        file_browser = FileBrowser()
        self.signal, self.sampling_rate = file_browser.browse_file(mode= 'music')
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
        self.plot_frequency_domain()
        

    def updateSignalView_timeDomain(self):
        """Plot the signal in the time domain."""
        if len(self.signal) > 0 and self.isPaused == False :
            self.PlotWidget_inputSignal.plotItem.setYRange(-1, 1)
            self.PlotWidget_inputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)
            #self.PlotWidget_outputSignal.plotItem.setYRange(-1, 1)
            self.PlotWidget_outputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)
        
            self.left_x_view += 1/10   # incrementing the left view smoothly by matching the update time of the timer
            self.right_x_view = self.left_x_view + 1
            
            if self.right_x_view > self.duration:
                self.timer.stop()
                self.isPaused = True   

    
    def changeMode (self):
        selected_index = self.comboBox_modeSelection.currentIndex()
        if selected_index == 0:
            self.startDefault()
            self.PlotWidget_fourier.showCanvas()
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
            
            self.label_1_Hz.setText("10 Hz")
            self.label_3_Hz.setText("30 Hz")
            self.label_4_Hz.setText("40 Hz")
            self.label_5_Hz.setText("50 Hz")
            self.label_6_Hz.setText("60 Hz")
            self.label_7_Hz.setText("70 Hz")
            self.label_8_Hz.setText("80 Hz")
            self.label_9_Hz.setText("90 Hz")
            self.label_10_Hz.setText("100 Hz")

            
        else:
            self.PlotWidget_outputSignal.clear()
            self.PlotWidget_inputSignal.clear()
            self.PlotWidget_inputSpectrogram.hideSpectrogram()
            self.PlotWidget_outputSpectrogram.hideSpectrogram()
            self.PlotWidget_fourier.hideCanvas()
            self.isPaused = True
            
            self.verticalSlider_1.hide()
            self.verticalSlider_3.hide()
            self.verticalSlider_5.hide()
            self.verticalSlider_7.hide()
            self.verticalSlider_9.hide()
            self.verticalSlider_10.hide()
            
            self.label_1_Hz.hide()
            self.label_3_Hz.hide()
            self.label_5_Hz.hide()
            self.label_7_Hz.hide()
            self.label_9_Hz.hide()
            self.label_10_Hz.hide()
            
            self.shown_sliders_indices = [1, 3, 5, 7]
            
            currDict = self.ranges[selected_index]   # the dictionary (corresponding to the chosen mode) containing ranges of frequencies for each slider from the list "ranges"
            loopCounter = 0
            for key in currDict:
                self.sliders[self.shown_sliders_indices[loopCounter]].setValue(10)  # initializing scale of each slider to be 1 (maximum)
                self.labels[self.shown_sliders_indices[loopCounter]].setText(key)   # adjusting label of each slider
                loopCounter += 1
            
            self.sliderFrequencyMap = {}  # contains each slider as a key, the starting and ending freqs (tuple) of its range of freqs as the value
            for i in range(len(self.shown_sliders_indices)):
                self.sliderFrequencyMap[self.sliders[self.shown_sliders_indices[i]]] = currDict[self.labels[self.shown_sliders_indices[i]].text()]   # output map:  {slider_1 : [0, 170] , slider_2: [180, 240], ...}

    def updateModifiedSignal(self):  # ma3aya kol slider b bdayet w nhayet el range of frequencies beta3o
        self.modified_signal = self.computeFourierTransform()
        self.output_time_values = np.linspace(start = 0, stop = self.duration, num = len(self.modified_signal))
        self.PlotWidget_outputSignal.clear()
        #self.PlotWidget_outputSignal.plotItem.setYRange(-1, 1)
        self.PlotWidget_outputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)
        self.PlotWidget_outputSignal.plot(self.output_time_values, self.modified_signal, pen = "b")
        
        
    def computeFourierTransform(self):
        """Compute the Fourier transform of the signal."""
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
                new_slider_magnitudes = self.magnitudes[slider_freq_indices] * (slider.value()/10) # new magnitudes in this range corresponding to the slider's value     
                self.freq_components[slider_freq_indices] = new_slider_magnitudes * np.exp(1j * self.phase_angles[slider_freq_indices]) # updating frequency components array in this range
        
        #print(f"length of frequencies array: {len(self.frequencies)}")  # for debugging
        print(f"frequencies corrsponding to last slider: {self.frequencies[slider_freq_indices]}")
        print(f"magnitudes corresponding to last slider: {new_slider_magnitudes}")
        
        modified_signal = self.invFourierTransform()
        return modified_signal




    def invFourierTransform(self):
        """Compute the inverse Fourier transform."""
        modified_signal = np.fft.ifft(self.freq_components).real
        return modified_signal

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
        self.timer.setInterval(int(100 / speed))

    def stopAndReset(self, reset):
        """Stop and reset the signal."""
        self.timer.stop()
        self.isPaused = True
        if reset:
            self.plotSignal()     

    def zoom(self, factor):
        """Zoom in or out on the signal."""
        self.PlotWidget_inputSignal.plotItem.getViewBox().scaleBy((factor, 1))
        # self.PlotWidget_outputSignal.plotItem.getViewBox().scaleBy((factor, 1))
       
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
    
    # def updateOutput(self):
    #     for i in range(0, 10):
    #         self.magnitudes[i] = self.sliders[i].value() / 10.0
                
    #     self.modified_signal = 0
    #     loopCounter = 0
    #     for i in range(10, 110, 10):
    #         self.modified_signal += self.magnitudes[loopCounter] * np.sin(2* np.pi * i * self.time_values)
    #         loopCounter +=1
        
    #     # Update the output signal in real-time
    #     self.PlotWidget_outputSignal.clear()  # Clear the previous plot
    #     self.PlotWidget_outputSignal.plot(self.time_values[ : self.curr_ptr + self.chunksize], self.modified_signal[ : self.curr_ptr + self.chunksize], pen='b')

    #     # If we're playing, don't stop the timer
    #     if not self.isPaused:
    #         self.togglePlayPause()

    #     self.PlotWidget_outputSpectrogram.update(self.magnitudes)
    #     self.plot_frequency_domain()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
