const int buttonPin = 2;
const int motorPin = 6;

unsigned long previousfoodmillis, motorpreviousMillis = 0UL;
unsigned long foodinterval = 600UL;

int food = 60;

int buttonState = 0;
int motorState = 0;
bool down = false;
int vibrateOn = 0;

int overfeed(int food) {
  if(food > 60){
      food = 60;
  } else if(food < 0){
    food = 0;
  }

    return food;
}

void setup() {
  // put your setup code here, to run once:

  pinMode(buttonPin, INPUT);
  pinMode(motorPin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  //TODO:
  //feeding, led light for happy/hungry (red hunger, green happy)
  //hunger total 60 drop every min, magnet as feeding mech
  //petting (touch capacitor)
  //feeding, use magnet, within 5s

  //sleep?

  buttonState = digitalRead(buttonPin);

  unsigned long currentMillis = millis();
  if(currentMillis - motorpreviousMillis > 1000UL){
      if (vibrateOn == 0){
        digitalWrite(motorPin, 1);
        vibrateOn =1;
        motorpreviousMillis = currentMillis;
      } else if (vibrateOn == 1){
        digitalWrite(motorPin, 0);
        vibrateOn =0;
        motorpreviousMillis = currentMillis;
      }
  }

  currentMillis = millis();
  if(currentMillis - previousfoodmillis > foodinterval){
    food -= 1;
    food = overfeed(food);
    previousfoodmillis = currentMillis;
    Serial.println(food);
  }

  if ((buttonState == HIGH) && (!down)){
    down = true;
    food += 20;
    food = overfeed(food);
    Serial.println("nom nom");
  } else if (buttonState == LOW) {
    down = false;
  }
}

