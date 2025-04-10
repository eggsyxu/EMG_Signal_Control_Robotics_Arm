import sys
import numpy as np
import serial
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QGridLayout, QHBoxLayout, QPushButton
)
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy.signal import iirnotch, lfilter

class SerialSignalViewer(QMainWindow):
    def __init__(self, port='/dev/cu.usbserial-2120', baudrate=115200,
                 sampling_rate=1000, duration=3):
        super().__init__()

        # Serial and signal settings
        self.port = port
        self.baudrate = baudrate
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.num_points = int(sampling_rate * duration)
        self.time_base = np.linspace(0, duration, self.num_points)

        # Channel definitions
        self.num_channels = 6
        self.channel_labels = [
            "A0 - Left Wrist", "A1 - Right Wrist", "A2 - Left Elbow",
            "A3 - Right Elbow", "A4 - Left Leg", "A5 - Right Leg"
        ]
        self.channel_actions = ['L', 'R', 'F', 'B', 'G', 'O']

        # Signal buffers and settings
        self.data = [np.zeros(self.num_points) for _ in range(self.num_channels)]
        self.thresholds = [85, 180, 100, 180, 400, 180]
        self.cooldown_time = 0.8
        self.priority_window = 1.0
        self.last_spike_time = [0] * self.num_channels
        self.spike_history = [[] for _ in range(self.num_channels)]

        # Filter setup
        self.b_notch, self.a_notch = iirnotch(60.0, 10.0, fs=sampling_rate)

        # Serial not yet open
        self.ser = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        grid_layout = QGridLayout()
        self.plots = []

        for i in range(self.num_channels):
            pw = pg.PlotWidget()
            pw.setTitle(self.channel_labels[i])
            pw.setYRange(0, 500)
            pw.setXRange(0, self.duration)
            pw.setMinimumHeight(250)
            curve = pw.plot(pen='g')
            self.plots.append(curve)
            row, col = i // 2, i % 2
            grid_layout.addWidget(pw, row, col)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Serial")
        self.stop_button = QPushButton("Stop Serial")
        self.reset_button = QPushButton("Reset Arm")

        self.start_button.clicked.connect(self.open_serial)
        self.stop_button.clicked.connect(self.close_serial)
        self.reset_button.clicked.connect(self.send_reset)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(grid_layout)
        main_layout.addLayout(button_layout)

    def open_serial(self):
        if self.ser is None or not self.ser.is_open:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                self.timer.start(1)
                print(f"Serial opened on {self.port}")
            except Exception as e:
                print(f"Failed to open serial port: {e}")

    def close_serial(self):
        if self.ser and self.ser.is_open:
            self.timer.stop()
            self.ser.close()
            print("Serial closed.")

    def send_reset(self):
        if self.ser and self.ser.is_open:
            print("Sending 'Z' to Arduino")
            self.ser.write(b'Z')

    def has_spike_nearby(self, history, now, window):
        """Check if any spike in history is within ±window seconds of now."""
        return any(abs(now - t) <= window for t in history)

    def update_plot(self):
        if not self.ser or not self.ser.is_open:
            return

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

        now = time.time()

        for i in range(self.num_channels):
            # Signal filtering and plotting
            self.data[i] = np.roll(self.data[i], -1)
            filtered = lfilter(self.b_notch, self.a_notch, [self.data[i][-2], values[i]])
            self.data[i][-1] = filtered[-1]
            self.plots[i].setData(self.time_base, self.data[i])

            # Spike detection with elbow priority
            if filtered[-1] > self.thresholds[i]:
                dt = now - self.last_spike_time[i]
                if dt > self.cooldown_time:
                    if i == 0 and self.has_spike_nearby(self.spike_history[2], now, self.priority_window):
                        continue
                    if i == 1 and self.has_spike_nearby(self.spike_history[3], now, self.priority_window):
                        continue

                    print(f"Burst on A{i} ({self.channel_labels[i]}) → Send '{self.channel_actions[i]}'")
                    self.last_spike_time[i] = now
                    self.spike_history[i].append(now)

                    if self.ser and self.ser.is_open:
                        self.ser.write(self.channel_actions[i].encode())

                    # Clean old spike times
                    self.spike_history[i] = [t for t in self.spike_history[i] if now - t <= 2.0]

    def closeEvent(self, event):
        self.close_serial()
        print("Serial port closed.")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = SerialSignalViewer(
        port='/dev/cu.usbserial-2120',
        baudrate=115200,
        sampling_rate=1000,
        duration=3
    )
    viewer.setWindowTitle("EMG Controller: 6-Channel Real-Time Viewer")
    viewer.resize(1800, 800)
    viewer.show()
    sys.exit(app.exec_())
