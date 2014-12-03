int incomingByte, postNumber, pinNumber, state;

void setup() {
  Serial.begin(115200);
  for (int i = 2; i <= 7; i++) {
    pinMode(i, OUTPUT);
  }
}

void loop() {
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();
    
    int postNumber = 7 & incomingByte;
    int pinNumber = postNumber + 2;
    
    int state = incomingByte >> 3;

    digitalWrite(pinNumber, state);
    
    Serial.print(pinNumber);
    Serial.print(":");
    Serial.print(state);
    
    if (pinNumber == 7) {
      Serial.print("\n");
    } else {
      Serial.print("/");
    }
  }
}
