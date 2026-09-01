/*
  Hand Gesture LED Controller — Arduino Side (2 LEDs)
  =====================================================
  Receives a 2-character string (e.g. "10\n") over Serial
  from the Python script and toggles 2 LEDs accordingly.

  Wiring:
    LED 1 (Index)  → Pin 2  (+ 220Ω resistor to GND)
    LED 2 (Middle) → Pin 3  (+ 220Ω resistor to GND)

  Protocol:
    Python sends: "10\n"
    '1' = LED ON, '0' = LED OFF
*/

// ── Pin definitions ──────────────────────────────────────
const int LED_PINS[2] = {2, 3};
const int NUM_LEDS    = 2;

// ── Setup ────────────────────────────────────────────────
void setup() {
  Serial.begin(9600);

  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }

  // Startup blink so you know Arduino is ready
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], HIGH);
    delay(200);
  }
  delay(300);
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], LOW);
    delay(200);
  }

  Serial.println("READY");
}

// ── Main loop ─────────────────────────────────────────────
void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // Validate: must be exactly 2 characters of '0' or '1'
    if (cmd.length() == NUM_LEDS) {
      bool valid = true;
      for (int i = 0; i < NUM_LEDS; i++) {
        if (cmd[i] != '0' && cmd[i] != '1') {
          valid = false;
          break;
        }
      }

      if (valid) {
        for (int i = 0; i < NUM_LEDS; i++) {
          digitalWrite(LED_PINS[i], cmd[i] == '1' ? HIGH : LOW);
        }

        Serial.print("LEDs: ");
        Serial.println(cmd);
      }
    }
  }
}
