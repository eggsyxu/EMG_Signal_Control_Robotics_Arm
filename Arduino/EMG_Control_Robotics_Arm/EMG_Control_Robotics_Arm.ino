#include <Servo.h>

// Declare servo objects
Servo sideServo;     // Left-right movement
Servo frontServo;    // Forward-backward movement
Servo grabServo;     // Gripping action

// Servo position variables
int sideAngle = 90;       // Initial angle for side servo
int frontAngle = 130;     // Initial angle for front servo
int grabAngle = 30;       // Initial angle for grab servo

// EMG analog input pins
const int emgPins[6] = {A0, A1, A2, A3, A4, A5};  // 6-channel EMG input

void setup() {
  Serial.begin(115200);  // Start serial communication

  // Attach servos to corresponding digital pins
  sideServo.attach(3);   // Side servo on D3
  frontServo.attach(5);  // Front servo on D5
  grabServo.attach(6);   // Grab servo on D6

  // Move servos to their initial positions
  sideServo.write(sideAngle);
  frontServo.write(frontAngle);
  grabServo.write(grabAngle);
}

void loop() {
  // === 1. Read and send all 6 EMG values ===
  for (int i = 0; i < 6; i++) {
    int value = analogRead(emgPins[i]);  // Read analog value from A0–A5
    Serial.print(value);                 // Send value
    if (i < 5) Serial.print(',');        // Add comma between values
  }
  Serial.println();                      // End line after 6 values

  // === 2. Check for incoming servo control commands ===
  if (Serial.available()) {
    char command = Serial.read();  // Read 1 character command

    // -- Side servo (left-right) --
    if (command == 'L') {
      sideAngle = min(180, sideAngle + 30);
      sideServo.write(sideAngle);
      delay(500);  // Allow time to move

    } else if (command == 'R') {
      sideAngle = max(0, sideAngle - 30);
      sideServo.write(sideAngle);
      delay(500);

    // -- Front servo (forward-backward) --
    } else if (command == 'F') {
      frontAngle = min(180, frontAngle + 25);
      frontServo.write(frontAngle);
      delay(500);

    } else if (command == 'B') {
      frontAngle = max(70, frontAngle - 25);  // Limit to avoid mechanical collision
      frontServo.write(frontAngle);
      delay(500);

    // -- Grab servo (open-close) --
    } else if (command == 'G') {
      grabAngle = min(90, grabAngle + 30);  // Limit to 90° max
      grabServo.write(grabAngle);
      delay(500);

    } else if (command == 'O') {
      grabAngle = max(0, grabAngle - 30);   // Limit to 0° min
      grabServo.write(grabAngle);
      delay(500);

    // -- Reset all servos to default positions --
    } else if (command == 'Z') {
      sideAngle = 90;
      frontAngle = 130;
      grabAngle = 30;

      sideServo.write(sideAngle);
      frontServo.write(frontAngle);
      grabServo.write(grabAngle);
      delay(500);
    }
  }

  delay(1);  // Maintain 1000 Hz EMG sampling rate
}
