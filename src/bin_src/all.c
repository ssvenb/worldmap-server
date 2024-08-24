#include <wiringPi.h>
#include <stdio.h>
#include <math.h>

#define SAFE 27
#define CLOCK 28
#define DATA 29

void activateAllPins() {
    pinMode(SAFE, OUTPUT);
    pinMode(CLOCK, OUTPUT);
    pinMode(DATA, OUTPUT);
}

void deactivateAllPins() {
    pinMode(SAFE, INPUT);
    pinMode(CLOCK, INPUT);
    pinMode(DATA, INPUT);
}

void triggerPin(int pin) {
    digitalWrite(pin, HIGH);
    delay(1);
    digitalWrite(pin, LOW);
}

void save() {
    triggerPin(SAFE);
}

void clock() {
    triggerPin(CLOCK);
}

void writeAll(int leds[], int size) {
    for (int reg = 0; reg < size / sizeof(int); reg++) {
        for (int i = 0; i < 16; i++) {
            digitalWrite(DATA, (leds[reg] >> i) & 1);
            clock();
        }
    }
    save();
}

int lightLedNo(int ledNo, int size) {
    int maxPinNo = 16;
    if (ledNo > maxPinNo * size) {
        return 1;
    }
    int leds[size];
    for (int i = 0; i < size; i++) {
        leds[i] = 0;
    }
    int regNo = size - 1 - (ledNo / maxPinNo);
    int pinNo =  maxPinNo - (ledNo % maxPinNo);
    leds[regNo] = pow(2, pinNo);
    writeAll(leds, sizeof(leds));
    return 0;
}

int main() {
    if(wiringPiSetup() == -1) {
        return 1;
    }
    activateAllPins();
    
    digitalWrite(SAFE, LOW);
    digitalWrite(CLOCK, LOW);

    int leds[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
    writeAll(leds, sizeof(leds));

    return 0;
}