void setup() {
  Serial.begin(115200);
  for (int i = 2; i <= 7; i++) {
    pinMode(i, OUTPUT);
  }
}

void loop() {
  for (int i = 2; i <= 7; i++) {
    for (int j = 2; j <= 7; j++) {
      Serial.print(j);
      Serial.print(":");
      Serial.print(j == i ? "1" : "0");
      Serial.print("/");
      digitalWrite(j, j == i ? HIGH : LOW);
    }
    Serial.println("");
    delay(1000);
  }
  
  for (int i = 0; i <= 1; i++) {
    for (int j = 2; j <= 7; j++) {
      Serial.print(j);
      Serial.print(":");
      Serial.print(i == 0 ? "1" : "0");
      Serial.print("/");
      digitalWrite(j, i == 0 ? HIGH : LOW);
    }
    Serial.println("");
    delay(1000);
  }
//  digitalWrite(7, HIGH);
//  delay(1000);
//  digitalWrite(7, LOW);
//  delay(1000);
}
