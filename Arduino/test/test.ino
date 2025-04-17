#include <Servo.h>

// Declare servo objects
Servo sideServo;     // Left-right movement
Servo frontServo;    // Forward-backward movement
Servo grabServo;     // Gripping action

// Servo position variables
int sideAngle = 90;
int frontAngle = 130;
int grabAngle = 0;

// EMG analog input pins (A0–A4 only)
const int emgPins[5] = {A0, A1, A2, A4, A5};

void setup() {
  Serial.begin(115200);

  sideServo.attach(3);
  frontServo.attach(5);
  grabServo.attach(6);

  sideServo.write(sideAngle);
  frontServo.write(frontAngle);
  grabServo.write(grabAngle);
}

void loop() {
  // === 1. Send 5-channel EMG values ===
  for (int i = 0; i < 5; i++) {
    int value = analogRead(emgPins[i]);
    Serial.print(value);
    if (i < 4) Serial.print(',');
  }
  Serial.println();

  // === 2. Receive servo commands ===
  if (Serial.available()) {
    char command = Serial.read();

    // -- Side servo (left-right) --
    if (command == 'L') {
      sideAngle = min(180, sideAngle + 30);
      sideServo.write(sideAngle);
      delay(500);

    } else if (command == 'R') {
      sideAngle = max(0, sideAngle - 30);
      sideServo.write(sideAngle);
      delay(500);

    // -- Front servo (forward-backward) --
    } else if (command == 'F') {
      frontAngle = min(180, frontAngle + 15);
      frontServo.write(frontAngle);
      delay(500);

    } else if (command == 'B') {
      frontAngle = max(70, frontAngle - 15);
      frontServo.write(frontAngle);
      delay(500);

    // -- Grab servo (close only) --
    } else if (command == 'G') {
      grabAngle = min(90, grabAngle + 15);
      grabServo.write(grabAngle);
      delay(500);

    // -- Reset all --
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

  delay(1);  // ~1000Hz EMG sampling
}
