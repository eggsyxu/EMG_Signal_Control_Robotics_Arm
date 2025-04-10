import serial
import time

SERIAL_PORT = '/dev/cu.usbserial-2120'  # 修改为你的串口设备
BAUD_RATE = 115200

# 打开串口连接
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)  # 等待 Arduino 重启

print("✅ Connected to Arduino.")
print("""
=== Control Commands ===
L → sideServo +30°
R → sideServo -30°
F → frontServo +25°
B → frontServo -20° (min 80)
G → grabServo +30° (max 90)
O → grabServo -30° (min 0)
Z → Reset all servos to default positions
Q → Quit
========================
""")

try:
    while True:
        command = input(">>> ").strip().upper()

        if command in ['L', 'R', 'F', 'B', 'G', 'O', 'Z']:
            ser.write((command + '\n').encode())  # 发送命令 + 换行
            print(f"Sent: {command}")

        elif command == 'Q':
            print("Exiting.")
            break

        else:
            print("Invalid command. Use: L R F B G O Z Q")

except KeyboardInterrupt:
    print("Interrupted. Closing serial.")

finally:
    ser.close()
    print("Serial connection closed.")
