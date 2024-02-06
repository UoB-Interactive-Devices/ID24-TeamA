#include <Wire.h>
#include <SPI.h>
#include <Adafruit_CAP1188.h>

// Reset Pin is used for I2C or SPI
#define CAP1188_RESET  9

// CS pin is used for software or hardware SPI
#define CAP1188_CS  10

// These are defined for software SPI, for hardware SPI, check your 
// board's SPI pins in the Arduino documentation
#define CAP1188_MOSI  11
#define CAP1188_MISO  12
#define CAP1188_CLK  13

// For I2C, connect SDA to your Arduino's SDA pin, SCL to SCL pin
// On UNO/Duemilanove/etc, SDA == Analog 4, SCL == Analog 5
// On Leonardo/Micro, SDA == Digital 2, SCL == Digital 3
// On Mega/ADK/Due, SDA == Digital 20, SCL == Digital 21

// Use I2C, no reset pin!
Adafruit_CAP1188 cap = Adafruit_CAP1188();

const int redPin = 5;
const int greenPin = 6;
const int bluePin = 10;
const int hallPin = 8;
const int motorPin = 12;

unsigned long previousfoodmillis, previouspetMillis, motorpreviousMillis = 0UL;
unsigned long foodinterval = 600UL;

int food = 255;
float petting = 255;

int hallState = 0;
int motorState = 0;
bool down = false;

int vibrateOn = 0;


float overfeed(float food) {
  if(food > 255){    //60 -> 255
      food = 255;
  } else if(food < 0){
    food = 0;
  }

    return food;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("CAP1188 test!");

  // Initialize the sensor, if using i2c you can pass in the i2c address
  // if (!cap.begin(0x28)) {
  if (!cap.begin()) {
    Serial.println("CAP1188 not found");
    while (1);
  }
  Serial.println("CAP1188 found!");

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(hallPin, INPUT);
  pinMode(motorPin, OUTPUT);  //INPUT -> OUTPUT
}

void loop() {
  // put your main code here, to run repeatedly:

  //TODO:
  //feeding, led light for happy/hungry (red hunger, green happy)
  //hunger total 60 drop every min, magnet as feeding mech
  //petting (touch capacitor)
  //feeding, use magnet, within 5s

  //sleep?

  hallState = digitalRead(hallPin);

  unsigned long currentMillis = millis();
  if(currentMillis - motorpreviousMillis > 1000UL){
      if (vibrateOn == 0){
        digitalWrite(motorPin, 1);
        vibrateOn = 1;
        motorpreviousMillis = currentMillis;
      } else if (vibrateOn == 1){
        digitalWrite(motorPin, 0);
        vibrateOn = 0;
        motorpreviousMillis = currentMillis;
      }
  }

  currentMillis = millis();
  if(currentMillis - previouspetMillis > foodinterval){
    petting -= 10;
    petting = overfeed(petting);
    previouspetMillis = currentMillis;
    Serial.print("pet: ");
    Serial.println(petting);
  }

  currentMillis = millis();
  if(currentMillis - previousfoodmillis > foodinterval){
    food -= 5;
    food = overfeed(food);
    previousfoodmillis = currentMillis;
    Serial.print("food: ");
    Serial.println(food);
  }

  // if (food > 40){
  //   setColor(0, 255, 0);
  // } else if (food <= 40 && food > 20) {
  //   setColor(255, 255, 0);
  // } else if (food <= 20) {
  //   setColor(255, 0, 0);
  // }

  setColor(255 - food, food, petting);

  if ((hallState == HIGH) && (!down)){
    down = true;
    food += 80;
    food = overfeed(food);
    Serial.println("nom nom");
  } else if (hallState == LOW) {
    down = false;
  }

  // Serial.println(digitalRead(hallPin));
  if (digitalRead(hallPin) == 0) {
    hallState = HIGH;
    setColor(0, 0, 255);         //changed digitalWrite() -> setColor()
  } else if (digitalRead(hallPin) == 1){
    hallState = LOW;
    // setColor(255, 0, 0);          //changed digitalWrite() -> setColor()
  }

  uint8_t touched = cap.touched();
  digitalWrite(motorPin, LOW);

  if (touched == 0) {
    // No touch detected
    return;
  }
  
  for (uint8_t i=0; i<8; i++) {
    if (touched & (1 << i)) {
      if (i == 6) {
        digitalWrite(motorPin, HIGH);
        petting += 0.05;
        petting = overfeed(petting);
        // Serial.println("brr");
      }
      // Serial.print("C"); Serial.print(i+1); Serial.print("\t");
    }
  }
  // Serial.println();
  // delay(50);
}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(redPin, redValue);
  analogWrite(greenPin, greenValue);
  analogWrite(bluePin, blueValue);
}
