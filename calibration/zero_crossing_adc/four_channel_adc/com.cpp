char number_seconds = 0;
uint32_t number_of_ticks = 0;

bool wait_for_first_byte() {
  while (!Serial.available()) {
     delay(100);
  }
  number_seconds = Serial.read();
  number_of_ticks = number_seconds * PWM_FREQUENCY;
  return true;
}