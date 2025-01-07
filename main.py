import sys
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from classes import FileBrowser
import scipy.fftpack as fft
from UITEAM15 import Ui_MainWindow  # Import the Ui_MainWindow class
import pyqtgraph as pg

class MainApp( Ui_MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setupUi(self) # Loads all components of the UI created using the designer
        #self.weinerButton = QtWidgets.QPushButton()
        self.magnitudes = [1] * 10
        self.sliders = [self.verticalSlider_1, self.verticalSlider_2, self.verticalSlider_3, self.verticalSlider_4, self.verticalSlider_5,
                        self.verticalSlider_6, self.verticalSlider_7, self.verticalSlider_8, self.verticalSlider_9, self.verticalSlider_10]
        self.labels = [self.label_1_Hz, self.label_2_Hz, self.label_3_Hz, self.label_4_Hz, self.label_5_Hz,
                       self.label_6_Hz, self.label_7_Hz, self.label_8_Hz, self.label_9_Hz, self.label_10_Hz]
        self.defaultMode = True
        self.modeChanged = False
        self.region = None
        self.setupUI() # Calls our custom method which links the UI elements
        
        self.retranslateUi(self)
        self.timer = QTimer()
        self.connectSignals()

        self.ranges = [
            {"empty" : ()},
            { # music and animal sounds # TODO: Fix the ranges when you find mixed music and animal sounds
                        "Dog": (0, 1300),# DONE
                        "Cat" : (1301, 4000), # DONE
                        "Bird" : (4001, 5000), # DONE
                        "Triangle" : (5001, 10000), # DONE
                        "Maracas" : (10001, 17250)
            },
            {
                # TODO: Fix the ranges when you find VOWELS
                "A" : (320,340 , 640,675,980,1000,1300, 1335,3286,3310,3950,3969),
                "O" : (215, 225, 270,325,600,630,925,940,1235,1260,2795,2810),
                "bass": (0,400), 
                "violin" : (570, 710),
                "gitar": (400,570, 700,890,  950,1250,  1320,1670,  1720,1820)
            },

        ]
        
        self.startDefault()

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
        self.len_sig = len(self.signal)
        if self.modeChanged:
            self.PlotWidget_inputSpectrogram.plotSpectrogram(None, 210)
            self.PlotWidget_outputSpectrogram.plotSpectrogram(None, 210)
            if self.checkBox_showSpectrogram.isChecked():
                self.PlotWidget_inputSpectrogram.showSpectrogram()
                self.PlotWidget_outputSpectrogram.showSpectrogram()
        self.timer.start(100)
        self.plot_frequency_domain()

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
        self.weinerButton.clicked.connect(self.updateModifiedSignal)  # to apply weiner every time we change the self.region position
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
        if self.comboBox_modeSelection.currentIndex() == 0:
            self.PlotWidget_fourier.plot_frequency_domain(self.modified_signal, self.sampling_rate , None, None )
        else:
            self.PlotWidget_fourier.plot_frequency_domain(None, None, self.modified_components,self.freq_bins , self.len_sig)
    
    def set_log_scale(self):
        self.PlotWidget_fourier.toggle_audiogram_scale()
        self.plot_frequency_domain()


    def uploadSignal(self):
        if self.comboBox_modeSelection.currentIndex() == 0:
            print("Choose a different mode!")
            return
        self.signal, self.sampling_rate = self.file_browser.browse_file()
        if self.signal is None or not self.sampling_rate:
            return
        if len(self.signal.shape)>1 :
            self.signal = self.signal[:,0]
        self.signal = self.signal[:15*self.sampling_rate]
        self.len_sig = len(self.signal)
    
        self.freq_bins = fft.fftfreq(self.len_sig, 1 / self.sampling_rate) # returns an array of frequency values corresponding to each sample in the FFT result
        self.freq_components = fft.fft(self.signal) # returns an array containing frequency components, their magnitudes, and their phases
        self.modified_components = self.freq_components
        # set all the sliders to its maximum value
        for i in range(10):
            self.sliders[i].setValue(10)
        self.plotSignal()


    def plotSignal(self): 
        self.PlotWidget_inputSignal.clear() 
        self.left_x_view = 0 # used in adjusting the left x view of the signal while running in cine mode
        self.right_x_view  = self.left_x_view + 1  # adjusting the right x view
        self.duration = (1/self.sampling_rate) * len(self.signal)
        self.time_values = np.linspace(start = 0, stop = self.duration, num = self.len_sig)   # duration = Ts (time bet each 2 samples) * number of samples (len(self.signal))
        self.output_time_values = self.time_values
        self.isPaused = False
        self.PlotWidget_inputSignal.plotItem.setYRange(-1, 1)
        self.PlotWidget_inputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)    
        self.PlotWidget_inputSignal.plot(self.time_values, self.signal, pen = "r")
        if self.comboBox_modeSelection.currentIndex() == 3:    # wiener mode
            self.PlotWidget_inputSignal.addItem(self.region)  # add the region on the input signal to apply the filter on it when self.updateModifedSignal is called
        self.updateModifiedSignal()  # starts the modified signal corresponding to the sliders values. (made it this way because when rewinding, sliders' values aren't necessiraly = 10, so op signal isn't necessiraly same as ip signal)
        self.timer.start(100)
        self.PlotWidget_inputSpectrogram.plotSpectrogram(self.signal, self.sampling_rate)
        self.PlotWidget_outputSpectrogram.plotSpectrogram(self.modified_signal, self.sampling_rate)
        if self.checkBox_showSpectrogram.isChecked():
            self.PlotWidget_inputSpectrogram.showSpectrogram()
            self.PlotWidget_outputSpectrogram.showSpectrogram()
        

    def updateSignalView_timeDomain(self):
        if hasattr(self, "signal") and self.isPaused == False:
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


                if self.curr_ptr + self.chunksize < self.len_sig:
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
    
    
    def apply_wiener_filter(self):
        if self.region is not None and self.signal is not None:
            print("enterd wiener method")
            try:
                # Get alpha from slider
                alpha = self.sliders[self.shown_sliders_indices[0]].value() 
                
                # Rest of your existing filter code, replacing the hardcoded alpha
                region_min, region_max = self.region.getRegion()
                sample_min = int(region_min * self.sampling_rate)
                sample_max = int(region_max * self.sampling_rate)
                noise = self.signal[sample_min:sample_max]
                
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
                
                self.modified_signal = np.zeros(len(self.signal))
                
                for i in range(0, len(self.signal) - nfft, hop):
                    segment = self.signal[i:i + nfft] * window
                    spectrum = np.fft.fft(segment)
                    power = np.abs(spectrum)**2
                    
                    eps = 1e-6
                    snr = np.maximum(power / (noise_psd + eps) - 1, 0)
                    H = snr / (snr + alpha)
                    
                    freq_smooth = np.linspace(0.5, 1.0, len(H)//2)
                    H[:len(H)//2] *= freq_smooth
                    H[len(H)//2:] *= freq_smooth[::-1]
                    
                    filtered = np.fft.ifft(spectrum * H)
                    self.modified_signal[i:i + nfft] += np.real(filtered) * window
                
                norm_factor = np.sum(np.hanning(nfft)**2)
                self.modified_signal /= norm_factor
                self.modified_signal /= np.max(np.abs(self.modified_signal))
                
                
            except Exception as e:
                print(f"Error applying Wiener filter: {str(e)}")
        
    def changeMode (self):
        self.modeChanged = True
        selected_index = self.comboBox_modeSelection.currentIndex()
        self.PlotWidget_inputSignal.clear()
        self.PlotWidget_outputSignal.clear()
        self.PlotWidget_fourier.clear_frequency_graph()

        if selected_index == 0:
            
            
            self.defaultMode = True
            self.region = None
            for i in range(len(self.sliders)):
                self.sliders[i].show()
                self.labels[i].show()
                sliderValue = (i + 1) * 10
                self.labels[i].setText(f"{sliderValue} Hz")
                self.sliders[i].setValue(10)
            self.startDefault()


        else:
            
            
            self.defaultMode = False
            self.PlotWidget_inputSpectrogram.hideSpectrogram()
            self.PlotWidget_outputSpectrogram.hideSpectrogram()
            self.checkBox_showSpectrogram.setChecked(False)
            self.isPaused = True
            self.left_x_view = 0 # used in adjusting the left x view of the signal while running in cine mode
            self.right_x_view  = self.left_x_view + 1  # adjusting the right x view
            if selected_index == 1:
                self.shown_sliders_indices = [0, 1, 2, 7, 8]  # indices of sliders for music mode
                self.region = None
            elif selected_index == 2:    
                self.shown_sliders_indices = [ 3, 5, 6, 7, 8]    # indices of sliders for VOWELS mode
                self.region = None
            else:
                self.shown_sliders_indices = [4] # indices of sliders for Weiner mode
                self.sliders[self.shown_sliders_indices[0]].setValue(10)
                self.labels[self.shown_sliders_indices[0]].setText("alpha")
                self.region = pg.LinearRegionItem()      # accessing the self.region as not to be none ( isn't appearing on ip signal yet)
                self.region.sigRegionChangeFinished.connect(self.apply_wiener_filter)   # call the apply wiener method when the region is moved
                self.sliders[self.shown_sliders_indices[0]].valueChanged.connect(self.updateModifiedSignal)
                
                ###########################################################################################################################################################################
            for i in range(len(self.sliders)):
                idxShown = False
                for idx in self.shown_sliders_indices:
                    if i == idx:
                        idxShown = True
                if not idxShown:
                    self.sliders[i].hide()
                    self.labels[i].hide()
                else:
                    self.sliders[i].show()
                    self.labels[i].show()
            if self.comboBox_modeSelection.currentIndex() != 3:                  
                currDict = self.ranges[selected_index]   # the dictionary (corresponding to the chosen mode) containing ranges of frequencies for each slider from the list "ranges"
                loopCounter = 0
                for key in currDict:
                    self.sliders[self.shown_sliders_indices[loopCounter]].setValue(10)  # initializing scale of each slider to be 1 (maximum)
                    self.labels[self.shown_sliders_indices[loopCounter]].setText(key)   # adjusting label of each slider
                    loopCounter += 1
            
            
            
    def updateModifiedSignal(self):
        # Modify the frequency freq_components based on slider values
        self.PlotWidget_outputSignal.clear()
            

        if self.defaultMode:

            for i in range(0, 10):
                self.magnitudes[i] = self.sliders[i].value() / 10.0
            self.modified_signal = 0
            loopCounter = 0
            for i in range(10, 110, 10):
                self.modified_signal += self.magnitudes[loopCounter] * np.sin(2* np.pi * i * self.time_values)
                loopCounter += 1
            self.PlotWidget_outputSignal.plot(self.time_values[ : self.curr_ptr + self.chunksize], self.modified_signal[ : self.curr_ptr + self.chunksize], pen='b')
            if not self.isPaused:
                self.togglePlayPause()
            self.PlotWidget_outputSpectrogram.update(None, self.magnitudes)
            return
   
        elif self.comboBox_modeSelection.currentIndex() != 3: # other modes except wiener
            if hasattr(self, "freq_components"):
                modified_freq_components = self.freq_components.copy()
            else:
                print("You Should Upload Signal First!")
                return

            loopCounter = 0
            current_mode = self.comboBox_modeSelection.currentIndex()
            for key in self.ranges[current_mode]:
                if len(self.ranges[current_mode][key]) > 2:
                    for i in range(0, len(self.ranges[current_mode][key]), 2):
                        low, high = self.ranges[current_mode][key][i], self.ranges[current_mode][key][i+1]
                        slider_value = self.sliders[self.shown_sliders_indices[loopCounter]].value() / 10.0
                        mask = (np.abs(self.freq_bins) >= low) & (np.abs(self.freq_bins) <= high)
                        modified_freq_components[mask] *= slider_value
                else:
                    low, high = self.ranges[current_mode][key]
                    slider_value = self.sliders[self.shown_sliders_indices[loopCounter]].value() / 10.0
                    mask = (np.abs(self.freq_bins) >= low) & (np.abs(self.freq_bins) <= high)
                    modified_freq_components[mask] *= slider_value
                loopCounter += 1  
            self.modified_components = modified_freq_components  
            self.modified_signal = np.real(fft.ifft(modified_freq_components)) 
        
        else:
            self.apply_wiener_filter() 
            print("wiener called from self.updateModifiedSignal method")
        self.file_browser.modified_signal = self.modified_signal
        self.output_time_values = np.linspace(start = 0, stop = self.duration, num = len(self.modified_signal))
        self.PlotWidget_outputSignal.plotItem.setXRange(self.left_x_view, self.right_x_view)
        self.PlotWidget_outputSignal.plot(self.output_time_values, self.modified_signal, pen = "b")
        self.PlotWidget_outputSpectrogram.update(self.modified_signal, [-1])
    
        self.plot_frequency_domain()




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
