#include <AFMotor.h> 
AF_DCMotor motorA(3);

void setup () { 
  motorA.setSpeed(210); // valor entre 0 e 255 
}

void loop () { 
  motorA.run(FORWARD);
  delay(500);
  motorA.run(BACKWARD);
  delay(700);
}
