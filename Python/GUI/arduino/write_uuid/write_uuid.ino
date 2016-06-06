#include <EEPROM.h>

char id[] = "bd0f5a84-a2eb-4ff3-9ff2-597bf3b2c20a";  // UUID4

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i=0; i < 36; i++) {
    EEPROM.write(i, id[i]);
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
