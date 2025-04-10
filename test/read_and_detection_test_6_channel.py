import sys
import numpy as np
import serial
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from scipy.signal import iirnotch, lfilter

class SerialSignalViewer(QMainWindow):
    def __init__(self, port='/dev/cu.usbserial-2120', baudrate=115200,
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

        self.thresholds = [85, 180, 100, 180, 400, 180]
        self.cooldown_time = 0.8
        self.priority_window = 1.0  # ±1s elbow suppression
        self.last_spike_time = [0] * self.num_channels
        self.spike_history = [[] for _ in range(self.num_channels)]  # keep timestamps

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
        self.timer.start(1)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QGridLayout(self.central_widget)
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
            layout.addWidget(pw, row, col)

    def has_spike_nearby(self, history, now, window):
        """Check if any spike in history is within ±window seconds of now."""
        return any(abs(now - t) <= window for t in history)

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

        now = time.time()

        for i in range(self.num_channels):
            # Filter and update plot
            self.data[i] = np.roll(self.data[i], -1)
            filtered = lfilter(self.b_notch, self.a_notch, [self.data[i][-2], values[i]])
            self.data[i][-1] = filtered[-1]
            self.plots[i].setData(self.time_base, self.data[i])

            # Burst detection
            if filtered[-1] > self.thresholds[i]:
                dt = now - self.last_spike_time[i]
                if dt > self.cooldown_time:

                    # Check suppression
                    if i == 0 and self.has_spike_nearby(self.spike_history[2], now, self.priority_window):
                        continue  # A2 dominates A0
                    if i == 1 and self.has_spike_nearby(self.spike_history[3], now, self.priority_window):
                        continue  # A3 dominates A1

                    print(f"⚡ Burst detected on channel A{i} ({self.channel_labels[i]})")
                    self.last_spike_time[i] = now
                    self.spike_history[i].append(now)

                    # Clean up old history
                    self.spike_history[i] = [t for t in self.spike_history[i] if now - t <= 2.0]

    def closeEvent(self, event):
        self.ser.close()
        print("🔌 Serial port closed.")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = SerialSignalViewer(
        port='/dev/cu.usbserial-2120',
        baudrate=115200,
        sampling_rate=1000,
        duration=3
    )
    viewer.setWindowTitle("EMG Viewer with ±1s Elbow Priority")
    viewer.resize(1800, 700)
    viewer.show()
    sys.exit(app.exec_())
