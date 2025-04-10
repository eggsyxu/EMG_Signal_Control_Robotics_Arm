import sys
import pandas as pd
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from scipy.signal import iirnotch, lfilter

class CSVSignalViewer(QtWidgets.QMainWindow):
    def __init__(self, csv_path, sampling_rate=1000, duration=3):
        super().__init__()
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.num_points = sampling_rate * duration
        self.time_base = np.linspace(0, duration, self.num_points)

        self.data = pd.read_csv(csv_path).values.T
        self.num_channels = self.data.shape[0]
        self.total_samples = self.data.shape[1]
        self.current_index = 0

        # Notch filter
        self.b_notch, self.a_notch = iirnotch(60.0, 10.0, fs=sampling_rate)

        self.init_ui()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)

    def init_ui(self):
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.plots = []

        self.plot_widgets = []
        for i in range(self.num_channels):
            pw = pg.PlotWidget()
            pw.setTitle(self.channel_labels[i] if hasattr(self, 'channel_labels') else f"A{i}")
            pw.setYRange(0, 1023)
            pw.setXRange(0, self.duration)
            curve = pw.plot(pen='g')
            self.plots.append(curve)
            self.plot_widgets.append(pw)
            row = i // 2
            col = i % 2
            grid_layout.addWidget(pw, row, col)

    def update_plot(self):
        end_index = self.current_index + self.num_points
        if end_index > self.total_samples:
            self.timer.stop()
            print("✅ Playback finished")
            return

        for i in range(self.num_channels):
            raw = self.data[i][self.current_index:end_index]
            filtered = lfilter(self.b_notch, self.a_notch, raw)
            self.plots[i].setData(self.time_base, filtered)

        self.current_index += self.num_points

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    viewer = CSVSignalViewer("simulated_30s_6channel_emg_v2.csv")
    viewer.setWindowTitle("Offline 6-Channel EMG Viewer")
    viewer.resize(1800, 900)
    viewer.show()
    sys.exit(app.exec_())
