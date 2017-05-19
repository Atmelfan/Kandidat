//
// Created by atmelfan on 2017-04-06.
//
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <avr/io.h>
#include "motors.h"
#include "gpa_scpi.h"


const char* next_arg2(const char* s){
    char last = *s;
    while(*s){
        if(isspace(last) && !isspace(*s)){
            if(*s == ';' || *s =='\0')
                return NULL;
            return s;
        }
        last = *s;
        s++;
    }
    if(*s == ';' || *s =='\0')
        return NULL;
    return s;
}

const char* scpi_motor_setduty1(const char* s){
    //scpi_print("A");
    uint16_t d = (uint16_t)strtoul(s, NULL, 10);
    if(d > MOTORS_PERIOD){
        //scpi_print("INVALID VALUE!");
        return scpi_nop(s);
    }else{
        scpi_print("");
    }
    motors_set_duty(0, MOTORS_PERIOD - d);
    return scpi_nop(s);
}

const char* scpi_motor_setduty2(const char* s){
    //scpi_print("B");
    uint16_t d = (uint16_t)strtoul(s, NULL, 10);
    if(d > MOTORS_PERIOD){
        scpi_print("INVALID VALUE!");
        return scpi_nop(s);
    }else{
        scpi_print("");
    }
    motors_set_duty(1, MOTORS_PERIOD - d);
    return scpi_nop(s);
}

const char *scpi_motor_setdir1(const char *s) {
    const char* tmp = next_arg2(s);
    if(strstr(tmp, "FORW") == tmp){
        scpi_print("GOING FORWARD!");
        motors_set_dir(0, 1);
    }else if(strstr(tmp, "BACK") == tmp){
        scpi_print("GOING BACKWARD!");
        motors_set_dir(0, 0);

    }else{
        scpi_print("INVALID DIRECTION!");
    }
    return scpi_nop(s);
}

const char *scpi_motor_setdir2(const char *s) {
    const char* tmp = next_arg2(s);
    if(strstr(tmp, "FORW") == tmp){
        scpi_print("GOING FORWARD!");
        motors_set_dir(1, 1);
    }else if(strstr(tmp, "BACK") == tmp){
        scpi_print("GOING BACKWARD!");
        motors_set_dir(1, 0);
    }else{
        scpi_print("INVALID DIRECTION!");
    }
    return scpi_nop(s);
}

const char *scpi_motor_setoff1(const char *s) {
    return NULL;
}

const char *scpi_motor_seton1(const char *s) {
    return NULL;
}

const char *scpi_motor_queryduty1(const char *s) {
    char  buf[16];
    itoa(AWEXC.OUTOVEN, buf, 16);
    scpi_print(buf);
    return scpi_nop(s);
}

const char *scpi_motor_queryduty2(const char *s) {
    return NULL;
}

