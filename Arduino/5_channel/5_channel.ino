const int emgPins[5] = {A0, A1, A2, A3, A4};  // 去掉 A5

void setup() {
  Serial.begin(115200);
}

void loop() {
  for (int i = 0; i < 5; i++) {
    int value = analogRead(emgPins[i]);
    Serial.print(value);
    if (i < 4) Serial.print(',');  // 最后一个值后不加逗号
  }
  Serial.println();  // 每组数据换行
  delay(1);          // 采样频率大约 1000Hz
}
