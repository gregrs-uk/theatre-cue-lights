const unsigned int FLASH_DELAY = 250;

const byte RESET = 0;
const byte STANDBY = 1;
const byte READY = 2;
const byte GO = 3;

class Channel
{ 
  byte pinA;
  byte pinB;
  byte pinC;

  public: byte status = RESET;

  bool redLedState = false;
  unsigned long previousMillis = 0;

  public:
  Channel(byte A, byte B, byte C) {
    pinA = A;
    pinB = B;
    pinC = C;
    
    pinMode(pinA, OUTPUT);
    pinMode(pinB, OUTPUT);
    pinMode(pinC, OUTPUT);
  }

  bool CheckAckButton() {
    pinMode(pinB, INPUT);
    digitalWrite(pinA, HIGH);
    digitalWrite(pinC, LOW);
    if (digitalRead(pinB) == LOW) { return true; }
    else { return false; }
  }

  void RedLed() {
    pinMode(pinB, OUTPUT);
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, HIGH);
    digitalWrite(pinC, HIGH);
  }

  void GreenLed() {
    pinMode(pinB, OUTPUT);
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, HIGH);
  }

  void ClearLeds() {
    pinMode(pinB, OUTPUT);
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(pinC, LOW);
  }

  void Reset() {
    status = RESET;
    ClearLeds();
  }
  
  void Standby() {
    status = STANDBY;
    // is it time to update the LED state yet?
    unsigned long currentMillis = millis();
    if(redLedState && (currentMillis - previousMillis >= FLASH_DELAY))
    {
      redLedState = false;
      previousMillis = currentMillis;
    }
    else if (!redLedState && (currentMillis - previousMillis >= FLASH_DELAY))
    {
      redLedState = true;
      previousMillis = currentMillis;
    }
    // either way, set the LED to the current state
    if (redLedState) {
      RedLed();
      delay(2);
    }
    else {
      ClearLeds();
      delay(2);
    }
  }

  void Ready() {
    status = READY;
    RedLed();
  }

  void Go() {
    status = GO;
    GreenLed();
  }
};

const byte numChannels = 6;

Channel chan[numChannels] = {
  Channel(2,3,4),
  Channel(5,6,7),
  Channel(8,9,10),
  Channel(11,12,13),
  Channel(A0,A1,A2),
  Channel(A3,A4,A5)
};

void setup() {
  Serial.begin(9600);
}

void loop() {
  // if ^ followed by two more bytes available from computer, read channel and status
  if (Serial.available() > 2 && Serial.read() == '^') {
    byte rxChannel = Serial.read() - '0'; // convert ASCII to numerical byte
    byte rxStatus = Serial.read() - '0'; // convert ASCII to numerical byte
    // check first byte
    if (rxChannel >= 0 && rxChannel < numChannels) {
      // if first byte is good, check second byte
      if (rxStatus >= RESET && rxStatus <= GO) {
        if (rxStatus == READY) { Serial.print("^Eonly ack button can set status to READY\n"); }
        else {
          chan[rxChannel].status = rxStatus;
          // acknowledge good status update by sending it back to computer
          Serial.print(String("^" + String(rxChannel) + String(rxStatus)));
        }
      }
      // if second byte is bad
      else { Serial.print("^Estatus not understood\n"); }
    }
    // if first byte is bad
    else { Serial.print("^Echannel not understood\n"); }
  }

  // for each channel
  for (byte num=0; num < numChannels; num++) {
    
    // if ack button is pressed
    if (chan[num].CheckAckButton()) {
      // if on STANDBY, go to READY
      if (chan[num].status == STANDBY) {
        chan[num].status = READY;
        Serial.print(String("^" + String(num) + String(READY)));
      }
      // if on GO, RESET channel
      else if (chan[num].status == GO) {
        chan[num].status = RESET;
        Serial.print(String("^" + String(num) + String(RESET)));
      }
    }
  
    // set LEDs based on status variable
    switch (chan[num].status) {
      case RESET:
        chan[num].Reset();
        break;
      case STANDBY:
        chan[num].Standby();
        break;
      case READY:
        chan[num].Ready();
        break;
      case GO:
        chan[num].Go();
        break;
    }
  }

  // prevent buggy behaviour
  delay(10);
}
