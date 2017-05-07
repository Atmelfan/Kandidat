//
// Created by atmelfan on 2017-04-10.
//

#include <stddef.h>
#include <stdio.h>
#include <util/delay.h>
#include "gpa_scpi.h"
#include "avg_adc.h"

#define DIST_VOLTAGE_DIVIDER (1.0/(1.0+3.9))

const char *scpi_distance_get0(const char *command) {
    static char buf[32];
    for (uint8_t i = 1; i <= 3; ++i) {
        sprintf(buf, "%f ", (1.0/DIST_VOLTAGE_DIVIDER)*ADC_TO_VOLTAGE(adc_read(i)));
        scpi_print(buf);
    }
    scpi_print("\r\n");
    return scpi_nop(command);
}

const char *scpi_line_get(const char *command) {
    static char buf[32];
    PORTF.DIRSET = 0x07 << 5;
    for (uint8_t i = 0; i < 8; ++i) {
        uint8_t x = (i & 0x07) << 5;
        PORTF.OUTCLR = 0x07 << 5;
        PORTF.OUTSET = x;
        _delay_ms(1);
        sprintf(buf, "%u ", adc_read(6));
        scpi_print(buf);
    }
    scpi_print("\r\n");
    return scpi_nop(command);
}
//nav:start;pick 0 5
