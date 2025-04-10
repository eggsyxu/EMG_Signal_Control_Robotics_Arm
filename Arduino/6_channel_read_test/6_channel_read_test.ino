const int emgPins[6] = {A0, A1, A2, A3, A4, A5};

void setup() {
  Serial.begin(115200);
}

void loop() {
  for (int i = 0; i < 6; i++) {
    int value = analogRead(emgPins[i]);
    Serial.print(value);
    if (i < 5) Serial.print(',');  // 逗号分隔
  }
  Serial.println();  // 换行
  delay(1);          // 控制采样频率（约 1000Hz）
}
