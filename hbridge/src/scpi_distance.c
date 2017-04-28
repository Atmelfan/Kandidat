//
// Created by atmelfan on 2017-04-10.
//

#include <stddef.h>
#include <stdio.h>
#include "gpa_scpi.h"
#include "avg_adc.h"

const char *scpi_distance_get0(const char *command) {
    static char buf[32];
    sprintf(buf, "%f", 5.0*ADC_TO_VOLTAGE(adc_read(1)));
    scpi_print(buf);
    return scpi_nop(command);
}
