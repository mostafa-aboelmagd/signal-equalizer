import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

class PlotWidget(FigureCanvas):
    def __init__(self, parent=None):
        # Initialize the Figure and the Canvas
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Amplitude')

    def plot(self, time, signal):
        self.ax.clear()  # Clear the previous plot
        self.ax.plot(time, signal)
        self.draw()  # Redraw the plot

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Set window title and layout
        self.setWindowTitle('Signal Summation Plot')
        layout = QtWidgets.QVBoxLayout(self)

        # Create the PlotWidget
        self.plot_widget = PlotWidget(self)
        layout.addWidget(self.plot_widget)

        # Define the signal parameters
        self.fs = 1000  # Sampling frequency
        self.t = np.arange(0, 1, 1 / self.fs)  # Time vector (1 second duration)
        self.magnitudes = [1] * 10  # Magnitudes of the sinusoids

        # Generate the signal and plot
        signal = self.generateSignal(self.magnitudes)
        self.plot_widget.plot(self.t, signal)

        self.setLayout(layout)
        self.setGeometry(100, 100, 600, 400)
        self.show()

    def generateSignal(self, magnitudes):
        # Generate the signal as a summation of sinusoids
        signal = 0
        loopCounter = 0
        for i in range(10, 110, 10):  # Frequencies from 10 to 100 Hz
            signal += magnitudes[loopCounter] * np.sin(2 * np.pi * i * self.t)
            loopCounter += 1
        return signal

# Main entry point for the application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
