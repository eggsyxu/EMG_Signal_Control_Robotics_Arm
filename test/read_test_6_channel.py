import sys
import numpy as np
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy.signal import iirnotch, lfilter

class SerialSignalViewer(QMainWindow):
    def __init__(self, port='/dev/cu.usbserial-120', baudrate=115200,
                 sampling_rate=1000, duration=3):
        super().__init__()

        self.sampling_rate = sampling_rate
        self.duration = duration
        self.num_points = int(sampling_rate * duration)
        self.time_base = np.linspace(0, duration, self.num_points)

        self.num_channels = 6
        self.channel_labels = [
            "A0 - Left Wrist", "A1 - Right Wrist", "A2 - Left Elbow",
            "A3 - Right Elbow", "A4 - Left Leg", "A5 - Right Leg"
        ]
        self.data = [np.zeros(self.num_points) for _ in range(self.num_channels)]

        self.b_notch, self.a_notch = iirnotch(60.0, 10.0, fs=sampling_rate)

        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"✅ Connected to {port} at {baudrate} baud")
        except Exception as e:
            print(f"❌ Failed to open serial port: {e}")
            sys.exit()

        self.init_ui()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1)  # 每毫秒采一组（1000Hz）

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QGridLayout(self.central_widget)
        self.plots = []

        for i in range(self.num_channels):
            pw = pg.PlotWidget()
            pw.setTitle(self.channel_labels[i])
            pw.setYRange(0, 600)
            pw.setXRange(0, self.duration)
            pw.setMinimumHeight(250)
            curve = pw.plot(pen='g')
            self.plots.append(curve)
            row, col = i // 2, i % 2
            layout.addWidget(pw, row, col)

    def update_plot(self):
        try:
            line = self.ser.readline().decode().strip()
            if not line:
                return
            values = line.split(',')
            if len(values) != self.num_channels:
                return
            values = [float(v) for v in values]
        except:
            return

        # 更新每个通道的滚动窗口
        for i in range(self.num_channels):
            self.data[i] = np.roll(self.data[i], -1)
            filtered = lfilter(self.b_notch, self.a_notch, [self.data[i][-2], values[i]])
            self.data[i][-1] = filtered[-1]
            self.plots[i].setData(self.time_base, self.data[i])

    def closeEvent(self, event):
        self.ser.close()
        print("🔌 Serial port closed.")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = SerialSignalViewer(
        port='/dev/cu.usbserial-2120',  # ⬅️ 修改为你的串口号
        baudrate=115200,
        sampling_rate=1000,
        duration=3
    )
    viewer.setWindowTitle("Real-Time 6-Channel EMG Viewer (Serial)")
    viewer.resize(1800, 900)
    viewer.show()
    sys.exit(app.exec_())
