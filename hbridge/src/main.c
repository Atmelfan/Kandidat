#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include "gpa_scpi.h"
#include "avg_adc.h"
#include <util/delay.h>

#define SCPI_USART USARTF0

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

void scpi_print(const char *s){
    usart_send(s);
}

void usart_init(){
    SCPI_USART.BAUDCTRLB = 0xD0;
    SCPI_USART.BAUDCTRLA = 131;
    SCPI_USART.CTRLC = USART_CHSIZE_8BIT_gc;
    SCPI_USART.CTRLA = USART_RXCINTLVL_LO_gc;
    SCPI_USART.CTRLB = USART_TXEN_bm | USART_RXEN_bm;
    PORTF.DIRSET = (1 << 3);
}


void twi_init(){
    /*Set TWI baud rate*/
    TWIC_MASTER_BAUD = 0xFF;
    /*SET WIEN, ENABLE and INTLVL bits high.*/
    TWIC_MASTER_CTRLA |= 0xD8;
    /*Force TWI bus idle mode.*/
    TWIC_MASTER_STATUS |= 0x01;
}

#define DISP_ADDR 0x7C

#define TWI_READ 0x01
#define TWI_WRITE 0x00


void twi_start(uint8_t addr){
    TWIC_MASTER_ADDR = addr;

    /*WAIT FOR THE WRITE INTERUPT FLAG TO SET HIGH*/
    while(!(TWIC_MASTER_STATUS & 64));


}

void twi_send(uint8_t data){
    TWIC_MASTER_DATA = data;
    while(!(TWIC_MASTER_STATUS & 64));
}

void twi_stop(){
    /* MASTER SENDS ACK AND ISSUES A STOP */
    TWIC_MASTER_CTRLC = 0x03;
}

void setup(){
    PMIC.CTRL = PMIC_LOLVLEN_bm|PMIC_MEDLVLEN_bm|PMIC_HILVLEN_bm;
    sei();
    usart_init();
    //usart_send("Hello world!\r\n");
    adc_init();
    PORTA.DIRSET = 0x01;
    PORTA.OUTSET = 0x01;
    _delay_ms(100);
    PORTA.OUTCLR = 0x01;


}
volatile uint8_t do_process = 0;
volatile static char buf[128];


void update(){
    //usart_send("B\n\r");
    if(do_process){
        scpi_execute((char*)buf);
        do_process = 0;
        PORTA.OUTTGL = 0x01;
    }

}



int main(void){
    setClockTo32MHz();
    setup();
    while(1){
        update();
    }
    return -1;
}



ISR(USARTF0_RXC_vect){
    static uint8_t indx = 0;
    static uint8_t mindx = 0;
    char tmp = SCPI_USART.DATA;
    if(do_process)
        return;
    buf[indx] = tmp;
/*    if(tmp == '\b' && indx > 0){
        indx --;
        usart_send("\b \b");
        return;
    }*/
    //usart_sendc(tmp);//Echo
    if(tmp == '\n'){
        buf[indx] = '\0';
        do_process = 1;
        indx = 0;
        mindx = 0;
    }else{
        indx++;
        mindx++;
    }
}