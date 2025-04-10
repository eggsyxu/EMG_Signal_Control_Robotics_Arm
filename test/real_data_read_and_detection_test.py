import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
)
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy.signal import iirnotch, lfilter, hilbert, butter, filtfilt

class CSVSignalPlotter(QMainWindow):
    def __init__(self, csv_path, refresh_interval=3000, duration=3):
        super().__init__()
        self.refresh_interval = refresh_interval
        self.duration = duration
        self.data = pd.read_csv(csv_path)
        self.time_array = self.data['time'].values
        self.signal_array = self.data['signal'].values

        # 基础参数
        self.sampling_rate = 1 / (self.time_array[1] - self.time_array[0])
        self.num_points = int(self.sampling_rate * self.duration)
        self.threshold = 0.12
        self.min_burst_duration = 0.05
        self.min_silence_duration = 0.05

        # 设计 60Hz Notch + 平滑滤波器
        self.b_notch, self.a_notch = iirnotch(60.0, 30.0, self.sampling_rate)
        self.b_lp, self.a_lp = butter(2, 5 / (0.5 * self.sampling_rate), btype='low')

        self.current_index = 0
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.plot_widget = pg.PlotWidget(self)
        self.curve = self.plot_widget.plot(pen='g')  # 只显示 notch 后信号
        self.plot_widget.setYRange(-0.5, 0.5)
        self.plot_widget.setXRange(0, self.duration)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.clicked.connect(self.start_timer)
        self.stop_button.clicked.connect(self.stop_timer)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.plot_widget)
        main_layout.addLayout(button_layout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.refresh_interval)

    def smooth_envelope(self, envelope):
        return filtfilt(self.b_lp, self.a_lp, envelope)

    def detect_bursts(self, envelope, t_window):
        is_active = envelope > self.threshold
        bursts = []
        start = None
        silence_counter = 0
        fs = self.sampling_rate

        for i, active in enumerate(is_active):
            if active:
                if start is None:
                    start = i
                silence_counter = 0
            elif start is not None:
                silence_counter += 1
                if silence_counter > self.min_silence_duration * fs:
                    end = i - silence_counter
                    duration = (end - start) / fs
                    if duration >= self.min_burst_duration:
                        t_start = t_window[start]
                        t_end = t_window[end]
                        bursts.append((t_start, t_end))
                    start = None
                    silence_counter = 0

        if start is not None:
            end = len(envelope)
            duration = (end - start) / fs
            if duration >= self.min_burst_duration:
                t_start = t_window[start]
                t_end = t_window[end - 1]
                bursts.append((t_start, t_end))

        return bursts

    def update_plot(self):
        end_index = self.current_index + self.num_points
        if end_index > len(self.signal_array):
            self.timer.stop()
            print("✅ Playback finished")
            return

        t = self.time_array[self.current_index:end_index]
        y = self.signal_array[self.current_index:end_index]

        # notch 滤波
        filtered = lfilter(self.b_notch, self.a_notch, y)

        # Hilbert 包络 + 平滑
        envelope = np.abs(hilbert(filtered))
        envelope = self.smooth_envelope(envelope)

        # burst 检测
        bursts = self.detect_bursts(envelope, t)
        for b_start, b_end in bursts:
            print(f"⚡ Burst from {b_start:.3f}s to {b_end:.3f}s")

        self.curve.setData(t - t[0], filtered)
        self.current_index += self.num_points

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(self.refresh_interval)

    def stop_timer(self):
        if self.timer.isActive():
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    csv_path = 'simulated_30s_emg.csv'
    window = CSVSignalPlotter(csv_path)
    window.setGeometry(100, 100, 800, 300)
    window.setWindowTitle('EMG Analyzer (Final Optimized)')
    window.show()
    sys.exit(app.exec_())
