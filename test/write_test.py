import serial
import time

# Replace this with your actual Arduino port
SERIAL_PORT = '/dev/cu.usbserial-120'
BAUD_RATE = 115200

# Open the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)  # Wait for Arduino to reset

print("Connected to Arduino.")
print("Enter 'L' to turn left, 'R' to turn right, 'Q' to quit.")

try:
    while True:
        command = input(">>> ").strip().upper()

        if command in ['L', 'R']:
            ser.write((command + '\n').encode())
            print(f"Sent: {command}")

        elif command == 'Q':
            print("Exiting.")
            break
        else:
            print("Invalid input. Use 'L', 'R', or 'Q'.")

except KeyboardInterrupt:
    print("Interrupted. Closing serial.")

finally:
    ser.close()
