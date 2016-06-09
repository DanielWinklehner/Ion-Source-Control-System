#include <EEPROM.h>

char id[] = "49ffb802-50c5-4194-879d-20a87bcfc6ef";  // UUID4

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
