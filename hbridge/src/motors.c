//
// Created by atmelfan on 2017-04-06.
//

#include <stdint.h>
#include <avr/io.h>
#include "motors.h"

uint16_t period = 0;
uint16_t duty_1 = 2000;
uint16_t duty_2 = 2000;

void motors_init() {
    PORTC.DIR = 0xFF;
    PORTC.OUT = 0x00;
}

void motors_start(uint16_t freq) {
    period = (uint16_t) (freq / (F_CPU));
    TCC0.PER = MOTORS_PERIOD;
    TCC0.CTRLB |= TC_WGMODE_SINGLESLOPE_gc;
    TCC0.CTRLA |= TC_CLKSEL_DIV1_gc;
    AWEXC.CTRL |= AWEX_DTICCAEN_bm | AWEX_DTICCBEN_bm| AWEX_DTICCCEN_bm| AWEX_DTICCDEN_bm;
}

void motors_stop() {
    AWEXC.CTRL &= ~(AWEX_DTICCAEN_bm | AWEX_DTICCBEN_bm| AWEX_DTICCCEN_bm| AWEX_DTICCDEN_bm);
    TCC0.CTRLA &= ~TC_CLKSEL_OFF_gc;
}

void motors_set_duty(uint8_t ch, uint16_t duty) {

    if(ch == 0){
        duty_1 = duty;
        TCC0.CCA = duty;
        TCC0.CCB = duty;
    }else{
        duty_2 = duty;
        TCC0.CCC = duty;
        TCC0.CCD = duty;
    }
}

void motors_set_dir(uint8_t ch, uint8_t direction) {
    motors_stop();
    if(ch == 0){
        AWEXC.OUTOVEN &= ~0x0F;
        PORTC.OUT &= ~0x0F;
        if(direction){
            AWEXC.OUTOVEN |= (0x03 << 0);
            PORTC.OUT |= (1 << 2);
        }else{
            AWEXC.OUTOVEN |= (0x03 << 2);
            PORTC.OUT |= (1 << 0);
        }
        motors_set_duty(0, duty_1);
    }else{
        AWEXC.OUTOVEN &= ~0xF0;
        PORTC.OUT &= ~0xF0;
        if(direction){
            AWEXC.OUTOVEN |= (0x30 << 0);
            PORTC.OUT |= (1 << 6);
        }else{
            AWEXC.OUTOVEN |= (0x30 << 2);
            PORTC.OUT |= (1 << 4);
        }
        motors_set_duty(1, duty_2);

    }
    motors_start(0);
}

motors_dir motors_get_dir(uint8_t ch) {
    
    return MOTOR_BACK;
}


void motors_enable(uint8_t ch, uint8_t enable){
    uint8_t tmp;
    if(ch == 0){
        tmp = TC0_CCAEN_bm;
    }else{
        tmp = TC0_CCCEN_bm;
    }

    if(enable) {
        TCC0.CTRLB |= tmp;
    }else{
        TCC0.CTRLB &= ~tmp;
    }
}




