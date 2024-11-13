import pandas as pd
import scipy.io.wavfile
import librosa
import soundfile as sf
import os


from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

import copy
from UITEAM15 import Ui_MainWindow  # Import the Ui_MainWindow class

class FileBrowser(Ui_MainWindow):
    global player
    def __init__(self, parent = None):
        self.parent = parent
        # Define the instruments and volumes
        
      
    def browse_file(self, mode):
        if mode == 'music':
            file_path, _ = QFileDialog.getOpenFileName(directory= "D:/Signal-Equalizer-DSP", filter= " wav files (*.wav)")
            signal, sampling_rate= librosa.load(file_path, sr= None)
            print(f"Signal path: {file_path}")
            return signal, sampling_rate

  

