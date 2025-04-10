import sys
import serial
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
)
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy.signal import iirnotch, lfilter

class SerialSignalPlotter(QMainWindow):
    def __init__(self, port='/dev/cu.usbserial-120', baudrate=115200,
                 refresh_interval=3000, sampling_rate=1000, duration=3):
        super().__init__()

        # 串口参数
        self.port = port
        self.baudrate = baudrate
        self.refresh_interval = refresh_interval
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.num_points = int(self.sampling_rate * self.duration)
        self.time_base = np.linspace(0, self.duration, self.num_points)

        # 60Hz Notch Filter
        self.notch_freq = 60.0
        self.quality_factor = 10.0
        self.b_notch, self.a_notch = iirnotch(w0=self.notch_freq, Q=self.quality_factor, fs=self.sampling_rate)

        # 打开串口
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"✅ Connected to {self.port} at {self.baudrate} baud")
        except Exception as e:
            print(f"❌ Failed to open serial port: {e}")
            sys.exit()

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 波形图
        self.plot_widget = pg.PlotWidget(self)
        self.curve = self.plot_widget.plot(pen='g')
        self.plot_widget.setYRange(-300, 300)
        self.plot_widget.setXRange(0, self.duration)

        # 控制按钮
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
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
        values = []
        while len(values) < self.num_points:
            try:
                line = self.ser.readline().decode().strip()
                if line:
                    value = float(line)
                    values.append(value)
            except:
                continue

        # Apply 60Hz notch filter
        filtered_values = lfilter(self.b_notch, self.a_notch, values)
        self.curve.setData(self.time_base, filtered_values)

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(self.refresh_interval)

    def stop_timer(self):
        if self.timer.isActive():
            self.timer.stop()

    def closeEvent(self, event):
        self.ser.close()
        print("🔌 Serial port closed.")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SerialSignalPlotter(
        port='/dev/cu.usbserial-120',  # ⬅️ 改成你真实设备路径
        baudrate=115200,
        refresh_interval=3000,
        sampling_rate=1000,
        duration=3
    )
    window.setGeometry(100, 100, 800, 300)
    window.setWindowTitle('Serial Oscilloscope with 60Hz Notch Filter')
    window.show()
    sys.exit(app.exec_())
