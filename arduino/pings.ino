#include <NewPing.h>

#define PING_INTERVAL 50
#define NUM_POSTS 6
#define SENSORS_PER_POST 2
#define MAX_DISTANCE 200

NewPing sonar[6][2] = {
  {NewPing(2, 2, MAX_DISTANCE), NewPing(3, 3, MAX_DISTANCE)},
  {NewPing(4, 4, MAX_DISTANCE), NewPing(5, 5, MAX_DISTANCE)},
  {NewPing(6, 6, MAX_DISTANCE), NewPing(7, 7, MAX_DISTANCE)},
  {NewPing(8, 8, MAX_DISTANCE), NewPing(9, 9, MAX_DISTANCE)},
  {NewPing(10, 10, MAX_DISTANCE), NewPing(11, 11, MAX_DISTANCE)},
  {NewPing(12, 12, MAX_DISTANCE), NewPing(13, 13, MAX_DISTANCE)}
};

void setup() {
  Serial.begin(115200);
}

void loop() {
  int inches;
  
  for (int i = 0; i < NUM_POSTS; i++) {
    for (int j = 0; j < SENSORS_PER_POST; j++) {
      inches = sonar[i][j].ping_in();
      Serial.print(i);
      Serial.print("/");
      Serial.print(j);
      Serial.print("/");
      Serial.println(inches);
      delay(PING_INTERVAL);
    }
  }
}
