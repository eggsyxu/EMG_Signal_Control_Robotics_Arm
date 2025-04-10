#include <Servo.h>

Servo sideServo;     // 左右（原来的）
Servo frontServo;    // 前后
Servo grabServo;     // 抓取

// 舵机当前角度
int sideAngle = 90;    // 左右舵机 初始 90°
int frontAngle = 130;  // 前后舵机 初始 130°
int grabAngle = 30;    // 抓取舵机 初始 30°

const int emgPin = A5;  // EMG 输入

void setup() {
  Serial.begin(115200);

  sideServo.attach(3);   // 左右舵机
  frontServo.attach(5);  // 前后舵机
  grabServo.attach(6);   // 抓取舵机

  // 初始化位置
  sideServo.write(sideAngle);
  frontServo.write(frontAngle);
  grabServo.write(grabAngle);
}

void loop() {
  // ========== 1. 读取 EMG 并发送 ==========
  int emgValue = analogRead(emgPin);
  Serial.println(emgValue);

  // ========== 2. 接收控制指令 ==========
  if (Serial.available()) {
    char command = Serial.read();

    // ---------- 左右舵机 ----------
    if (command == 'L') {
      sideAngle = min(180, sideAngle + 30);
      sideServo.write(sideAngle);
      delay(500);
    } else if (command == 'R') {
      sideAngle = max(0, sideAngle - 30);
      sideServo.write(sideAngle);
      delay(500);
    }

    // ---------- 前后舵机 ----------
    else if (command == 'F') {
      frontAngle = min(180, frontAngle + 25);
      frontServo.write(frontAngle);
      delay(500);
    } else if (command == 'B') {
      frontAngle = max(70, frontAngle - 25);
      frontServo.write(frontAngle);
      delay(500);
    }

    // ---------- 抓取舵机 ----------
    else if (command == 'G') {
      grabAngle = min(90, grabAngle + 30);
      grabServo.write(grabAngle);
      delay(500);
    } else if (command == 'O') {
      grabAngle = max(0, grabAngle - 30);
      grabServo.write(grabAngle);
      delay(500);
    }

    else if (command == 'Z') {
      sideAngle = 90;
      frontAngle = 130;
      grabAngle = 30;

      sideServo.write(sideAngle);
      frontServo.write(frontAngle);
      grabServo.write(grabAngle);

      delay(500);  // 可选：给舵机时间归位
}
  }

  delay(1);  // 保持 EMG 采样频率为 1000Hz
}
