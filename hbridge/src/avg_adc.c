//
// Created by atmelfan on 2017-04-10.
//

#include "avg_adc.h"
#include <avr/pgmspace.h>

uint8_t ReadSignatureByte(uint16_t Address)
{
    NVM_CMD = NVM_CMD_READ_CALIB_ROW_gc;
    uint8_t Result;
    Result = pgm_read_byte((uint8_t *)Address);
    NVM_CMD = NVM_CMD_NO_OPERATION_gc;
    return Result;
}

void adc_init() {
    ADCA.CTRLA = ADC_ENABLE_bm;
    ADCA.CTRLB = 0;
    ADCA.PRESCALER = ADC_PRESCALER_DIV512_gc;
    ADCA.CALL = ReadSignatureByte(0x20) ; //ADC Calibration Byte 0
    ADCA.CALH = ReadSignatureByte(0x21) ; //ADC Calibration Byte 1
    ADCA.REFCTRL = ADC_VREF;
    ADCA.CH0.CTRL = ADC_CH_GAIN_1X_gc | ADC_CH_INPUTMODE_SINGLEENDED_gc ; // Gain = 1, Single Ended
    ADCA.CH0.MUXCTRL = (0<<3);
    ADCA.CH0.INTCTRL = 0 ; // No interrupt
}

uint16_t adc_read(uint8_t ch) {
    ADCA.CH0.MUXCTRL = (ch<<3);
    ADCA.CH0.CTRL |= ADC_CH_START_bm;
    while (ADCA.INTFLAGS==0) ; // Wait for complete
    ADCA.INTFLAGS |= ADC_CH_CHIF_bm;
    return ADCA.CH0RES;
}


