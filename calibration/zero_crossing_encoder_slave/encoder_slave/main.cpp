#include <Arduino.h>
#include <imxrt.h>

volatile uint32_t TIME_CTR = 0;

int DEBOUNCE_DISTANCE_RESET = 1;
elapsedMicros delta_time;

void MASTER_RESET_FALLING() {
  // debounce
  bool last_state = false;
  for (int i = 0; i < DEBOUNCE_DISTANCE_RESET; i++) {
    bool state = digitalReadFast(PIN_TEENSY_SLAVE_RESET);
    if (state != LOW) {
      return;
    }
  }
  TIME_CTR = 0;
  delta_time = 0;
}

int DEBOUNCE_DISTANCE_CLK = 0;

void MASTER_CLK_FALLING() {
  // without debounce this is probably noisy!
  cli(); // suppress master reset and master clock, code must complete in time or else sync issues! TESTME
  // inc time
  TIME_CTR++;
  // take encoder reading
  uint16_t value = 0;
  bool angle_read_parity = as5147p_get_sensor_value(value);
  // log results to host
  log_encoder_ascii(TIME_CTR, value, delta_time);
  // allow interrupts again TESTME
  sei(); 
}


void encoder_slave_setup() {
  pinMode(PIN_TEENSY_SLAVE_CLK, INPUT);
  pinMode(PIN_TEENSY_SLAVE_RESET, INPUT);

  attachInterrupt(digitalPinToInterrupt(PIN_TEENSY_SLAVE_RESET), MASTER_RESET_FALLING, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_TEENSY_SLAVE_CLK), MASTER_CLK_FALLING, FALLING);

  // setup encoder
  as5147p_setup();
}

