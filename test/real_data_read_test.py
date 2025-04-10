import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
)
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

class CSVSignalPlotter(QMainWindow):
    def __init__(self, csv_path, refresh_interval=3000, duration=3):
        super().__init__()
        self.refresh_interval = refresh_interval
        self.duration = duration
        self.data = pd.read_csv(csv_path)
        self.time_array = self.data['time'].values
        self.signal_array = self.data['signal'].values

        # 从时间推算采样率
        self.sampling_rate = 1 / (self.time_array[1] - self.time_array[0])
        self.num_points = int(self.sampling_rate * self.duration)

        self.current_index = 0
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.plot_widget = pg.PlotWidget(self)
        self.curve = self.plot_widget.plot(pen='g')
        self.plot_widget.setYRange(-2, 2)
        self.plot_widget.setXRange(0, self.duration)

        # 按钮
        self.start_button = QPushButton("开始")
        self.stop_button = QPushButton("停止")
        self.start_button.clicked.connect(self.start_timer)
        self.stop_button.clicked.connect(self.stop_timer)

        # 布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.plot_widget)
        main_layout.addLayout(button_layout)

        # 定时器
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.refresh_interval)

    def update_plot(self):
        end_index = self.current_index + self.num_points
        if end_index > len(self.signal_array):
            self.timer.stop()
            print("✅ 数据播放结束")
            return

        t = self.time_array[self.current_index:end_index]
        y = self.signal_array[self.current_index:end_index]

        self.curve.setData(t - t[0], y)  # 重设时间轴从0开始
        self.current_index += self.num_points  # 前进到下一段

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(self.refresh_interval)

    def stop_timer(self):
        if self.timer.isActive():
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 替换成你下载后的 CSV 文件路径
    csv_path = 'simulated_30s_emg.csv'  # 如果和代码在同一目录，直接这样写；否则使用完整路径
    window = CSVSignalPlotter(csv_path)
    window.setGeometry(100, 100, 800, 300)
    window.setWindowTitle('CSV Playback Oscilloscope')
    window.show()
    sys.exit(app.exec_())
