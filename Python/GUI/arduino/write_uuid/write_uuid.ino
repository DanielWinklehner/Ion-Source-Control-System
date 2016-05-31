#include <EEPROM.h>

char id[] = "cf436e6b-ba3d-479a-b221-bc387c37b858";  // UUID4

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
