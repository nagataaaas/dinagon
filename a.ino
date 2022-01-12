#include <LiquidCrystal.h>
#include <TimerOne.h>

const int rs = 7, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
volatile int Btn[4], Ain;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

int failed = 0;

const int maximum_step = 10;
int move_direction = 0; // 0: neutral, -1: left, 1: right
int remain_step = 0;

int stick_man_tick = 0;
int stick_man_tick_per_move = 0; // level+1 -> 2, 3, 4, 5
int stick_man_position=0;

const int analogMax = 1024;
const int BarWidth = 7;
int barX = 0;


byte smile[8] = {
  B01110,
  B11111,
  B01110,
  B00100,
  B01110,
  B10101,
  B01010,
  B10001,
};

byte cry[8] = {
  B01110,
  B11111,
  B01110,
  B10101,
  B01110,
  B00100,
  B01010,
  B10001,
};

byte bar[8] = {
  B11111,
  B10101,
  B11111,
  B00000,
  B00000,
  B00000,
  B00000,
  B00000,
};

int getBarPosition() {
  return Ain / (1024.0 / (17 - BarWidth));
}

void TimerInt(void) {
  Ain=analogRead(A0);
  Btn[0]=digitalRead(A1);
  Btn[1]=digitalRead(A2);
  Btn[2]=digitalRead(A3);
  Btn[3]=digitalRead(A4);
}

void setup() {
  pinMode(9,OUTPUT);
  pinMode(10,OUTPUT);
  pinMode(11,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
  pinMode(A1,INPUT);
  pinMode(A2,INPUT);
  pinMode(A3,INPUT);
  pinMode(A4,INPUT);
  lcd.begin(16, 2);
  lcd.createChar(0, smile);
  lcd.createChar(1, cry);
  lcd.createChar(2, bar);
  Timer1.initialize(2000);
  Timer1.attachInterrupt(TimerInt);
  randomSeed(Ain);
  barX = getBarPosition();
  stick_man_position = barX + (BarWidth / 2);
}

void input() {
  int i;
  if (stick_man_tick_per_move == 0){ // not started
    for (i=0; i<4; i++){
      if (Btn[i] == LOW){
        stick_man_tick_per_move = i + 2;
        return;
      }
    }
  } else {
    barX = getBarPosition();
  }
}

void move() {
  if (remain_step <= 0){
    move_direction = -2 * random(2) + 1;
    if (move_direction == -1) remain_step = random(min(stick_man_position+1, maximum_step));
    else remain_step = random(min(16-stick_man_position, maximum_step));
  }
  stick_man_tick++;

  if (stick_man_tick % stick_man_tick_per_move == 0) {
      stick_man_position += move_direction;
      remain_step--;
      if(stick_man_position<0) stick_man_position=0;
      if(stick_man_position>15) stick_man_position=15;
  }
}

int check_failed() {
  if (stick_man_position < barX) return 1;
  if ((barX + BarWidth - 1) < stick_man_position) return 1;
  return 0;
}

void draw() {

  // stick man
  if (failed){
    lcd.setCursor(stick_man_position, 1);
    lcd.write((byte)0x01);
    lcd.setCursor(3, 0);
    lcd.print("failure...");
  } else {
    lcd.setCursor(stick_man_position, 0);
    lcd.write((byte)0x00);
  }

  // bar
  int i;
  for (i=0; i<BarWidth; i++){
    lcd.setCursor(barX+i, 1);
    lcd.write((byte)0x02);
  }

  //  clear
  delay(20);
  lcd.clear();
}

void loop() {
  if (failed == 0){
    input();
    move();
  }
  draw();

  if (check_failed()){
    failed = 1;
  }
  delay(30);
}