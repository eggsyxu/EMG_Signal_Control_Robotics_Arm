import sys
import numpy as np
import serial
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import pyqtgraph as pg
from scipy.signal import iirnotch, lfilter

class SerialReaderThread(QThread):
    data_received = pyqtSignal(list)
    burst_detected = pyqtSignal(str)

    def __init__(self, port, baudrate, num_channels, thresholds, cooldown_time, priority_window, channel_actions):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.num_channels = num_channels
        self.thresholds = thresholds
        self.cooldown_time = cooldown_time
        self.priority_window = priority_window
        self.channel_actions = channel_actions

        self.last_spike_time = [0] * self.num_channels
        self.spike_history = [[] for _ in range(self.num_channels)]
        self.running = True

        self.b_notch, self.a_notch = iirnotch(60.0, 10.0, fs=1000)

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1, write_timeout=0.1)
            print(f"✅ Connected to {self.port} at {self.baudrate} baud")
        except Exception as e:
            print(f"❌ Serial open failed: {e}")
            self.ser = None

    def run(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode().strip()
                values = list(map(float, line.split(',')))
                if len(values) != self.num_channels:
                    continue

                now = time.time()
                filtered = []
                for i in range(self.num_channels):
                    x = values[i]
                    y = lfilter(self.b_notch, self.a_notch, [x, x])[-1]
                    filtered.append(y)

                    if y > self.thresholds[i]:
                        dt = now - self.last_spike_time[i]
                        if dt > self.cooldown_time:
                            # elbow priority check
                            if i == 0 and self._has_spike_nearby(self.spike_history[2], now):
                                continue
                            if i == 1 and self._has_spike_nearby(self.spike_history[3], now):
                                continue

                            self.last_spike_time[i] = now
                            self.spike_history[i].append(now)
                            self.spike_history[i] = [t for t in self.spike_history[i] if now - t <= 2.0]

                            action = self.channel_actions[i]
                            self.burst_detected.emit(action)
                            try:
                                self.ser.write(action.encode())
                            except Exception as e:
                                print(f"⚠️ Write failed: {e}")

                self.data_received.emit(filtered)

            except Exception as e:
                continue

    def _has_spike_nearby(self, history, now):
        return any(abs(now - t) <= self.priority_window for t in history)

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()

class SerialSignalViewer(QMainWindow):
    def __init__(self, port='/dev/cu.usbserial-2120', baudrate=115200):
        super().__init__()

        self.num_channels = 5
        self.channel_labels = [
            "A0 - Left Wrist", "A1 - Right Wrist", "A2 - Left Elbow",
            "A3 - Right Elbow", "A4 - Left Leg"
        ]
        self.channel_actions = ['L', 'R', 'F', 'B', 'G']
        self.thresholds = [40, 18, 13, 13, 15]
        self.cooldown_time = 0.8
        self.priority_window = 1.0

        self.duration = 3
        self.sampling_rate = 1000
        self.num_points = int(self.sampling_rate * self.duration)
        self.time_base = np.linspace(0, self.duration, self.num_points)

        self.data = [np.zeros(self.num_points) for _ in range(self.num_channels)]

        self.init_ui()

        self.reader = SerialReaderThread(
            port, baudrate, self.num_channels,
            self.thresholds, self.cooldown_time,
            self.priority_window, self.channel_actions
        )
        self.reader.data_received.connect(self.update_plot)
        self.reader.burst_detected.connect(self.print_action)
        self.reader.start()

        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.refresh_plot)
        self.plot_timer.start(50)  # 20Hz UI refresh

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        grid_layout = QGridLayout()
        self.plots = []
        for i in range(self.num_channels):
            pw = pg.PlotWidget()
            pw.setTitle(self.channel_labels[i])
            pw.setYRange(0, 50)
            pw.setXRange(0, self.duration)
            pw.setMinimumHeight(200)
            curve = pw.plot(pen='g')
            self.plots.append(curve)
            grid_layout.addWidget(pw, i // 2, i % 2)

        layout.addLayout(grid_layout)

    def update_plot(self, values):
        for i in range(self.num_channels):
            self.data[i] = np.roll(self.data[i], -1)
            self.data[i][-1] = values[i]

    def refresh_plot(self):
        for i in range(self.num_channels):
            self.plots[i].setData(self.time_base, self.data[i])

    def print_action(self, action):
        print(f"🎯 Sent action: '{action}'")

    def closeEvent(self, event):
        self.reader.stop()
        print("🔌 Serial closed.")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = SerialSignalViewer()
    viewer.setWindowTitle("EMG Viewer — Threaded, Smooth")
    viewer.resize(1800, 800)
    viewer.show()
    sys.exit(app.exec_())
