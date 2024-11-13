     y_values = signal[self.curr_ptr : self.end_ptr]
            time_values = np.arange(len(y_values))
            
            self.PlotWidget_inputSignal.plotItem.setXRange(self.curr_ptr, self.end_ptr)
            self.PlotWidget_inputSignal.plot(time_values, y_values, pen = 'r')
            self.curr_ptr += 5
            self.end_ptr += 5