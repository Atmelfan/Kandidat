#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include "gpa_scpi.h"
#include "motors.h"

#define SCPI_USART USARTE0

void setClockTo32MHz() {
    CCP = CCP_IOREG_gc;              // disable register security for oscillator update
    OSC.CTRL = OSC_RC32MEN_bm;       // enable 32MHz oscillator
    while(!(OSC.STATUS & OSC_RC32MRDY_bm)); // wait for oscillator to be ready
    CCP = CCP_IOREG_gc;              // disable register security for clock update
    CLK.CTRL = CLK_SCLKSEL_RC32M_gc; // switch to 32MHz clock
}

void usart_sendc(char c){
    while( !(SCPI_USART.STATUS & USART_DREIF_bm) ); //Wait until DATA buffer is empty
    SCPI_USART.DATA = c;
}

void usart_send(const char* s){
    while(*s){
        usart_sendc(*s);
        s++;
    }
}

void usart_int(uint16_t i, uint8_t base){
    char  buf[16];
    itoa(i, buf, base);
    usart_send(buf);
}

void scpi_print(const char* s){
    usart_send(s);
    usart_sendc('\n');
    usart_sendc('\r');

}

void usart_init(){
    SCPI_USART.BAUDCTRLB = 0xD0;
    SCPI_USART.BAUDCTRLA = 131;
    SCPI_USART.CTRLC = USART_CHSIZE_8BIT_gc;
    SCPI_USART.CTRLA = USART_RXCINTLVL_LO_gc;
    SCPI_USART.CTRLB = USART_TXEN_bm | USART_RXEN_bm;
    PORTE.DIRSET = (1 << 3);
}

void setup(){
    PMIC.CTRL = PMIC_LOLVLEN_bm|PMIC_MEDLVLEN_bm|PMIC_HILVLEN_bm;
    sei();
    usart_init();
    usart_send("Hello world!\n\r");

    motors_init();
    motors_start(0);
    motors_set_duty(0, MOTORS_PERIOD); motors_set_dir(0, MOTOR_FORW);
    motors_set_duty(1, MOTORS_PERIOD); motors_set_dir(1, MOTOR_FORW);
}

void update(){

}



int main(void){
    setClockTo32MHz();
    setup();
    while(1){
        update();
    }
    return -1;
}




ISR(USARTE0_RXC_vect){
    static char buf[64];
    static uint8_t indx = 0;
    static uint8_t mindx = 0;
    char tmp = SCPI_USART.DATA;
    buf[indx] = tmp;
    if(tmp == '\b' && indx > 0){
        indx --;
        usart_send("\b \b");
        return;
    }
    usart_sendc(tmp);//Echo
    if(tmp == '\r'){
        buf[indx] = '\0';
        scpi_execute(buf);
        indx = mindx = 0;
    }else{
        indx++;
        mindx++;
    }
}