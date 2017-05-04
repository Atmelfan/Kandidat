//
// Created by atmelfan on 2017-04-06.
//

#ifndef AVR_CLION_MOTORS_H
#define AVR_CLION_MOTORS_H

#include <stdint.h>
#define MOTORS_PERIOD 2000

typedef enum {
    MOTOR_FORW = 1,
    MOTOR_BACK = 0
} motors_dir;

void motors_init();

void motors_start(uint16_t freq);
void motors_stop();

void motors_set_dir(uint8_t ch, uint8_t direction);
motors_dir motors_get_dir(uint8_t ch);
void motors_set_duty(uint8_t ch, uint16_t duty);
//uint16_t motors_get_duty(uint8_t ch)





#endif //AVR_CLION_MOTORS_H
