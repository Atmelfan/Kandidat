//
// Created by atmelfan on 2017-02-06.
//

#ifndef SCPI_GPA_SCPI_H
#define SCPI_GPA_SCPI_H

#include "stdlib.h"
#include "motors_scpi.h"

#define SCPI_IDN "AGV3 Motor Driver v0.1"

struct scpi_command;

struct scpi_command{
    const char* name;
    char optional;
    int num_subcommands;
    struct scpi_command* subcommands;
    const char* (*scpi_handler)(const char*);
    const char* (*scpi_query)(const char*);
};

typedef struct scpi_command scpi_command;

/**
 * Prints s to console
 * @param s
 */
extern void scpi_print(const char* s);


const char* compare_command(const char* str, const char* command);

const char* next_arg();

void scpi_execute(const char* command);

/*************Default handlers*************/
const char* scpi_nop(const char *command);
const char* scpi_query_nyi(const char* command);
const char* scpi_handler_nyi(const char* command);
const char* scpi_idn(const char* command);
const char* scpi_clear(const char* command);



#define SCPI_DIR .scpi_handler = NULL, .scpi_query = NULL


static struct scpi_command scpi_commands[] = {
    {.name = "CH1", SCPI_DIR, .num_subcommands = 3,
        .subcommands = (scpi_command*) &(scpi_command[]) {
            {.name="VELocity", .scpi_handler=scpi_motor_setduty1, .scpi_query=scpi_motor_queryduty1, .subcommands = NULL},
            {.name="DIRection", .scpi_handler=scpi_motor_setdir1, .scpi_query=scpi_query_nyi, .subcommands = NULL},
            {.name="CURRent", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL}
        }
    },
    {.name = "CH2", SCPI_DIR, .num_subcommands = 3,
        .subcommands = (scpi_command*) &(scpi_command[]) {
            {.name="VELocity", .scpi_handler=scpi_motor_setduty2, .scpi_query=scpi_query_nyi, .subcommands = NULL},
            {.name="DIRection", .scpi_handler=scpi_motor_setdir2, .scpi_query=scpi_query_nyi, .subcommands = NULL},
            {.name="CURRent", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL}
        }
    },
    /**
     * Command: NAVigate
     * Not callable nor queryable
     * Contains subcommands related to navigation
     */
    {.name = "SYStem", SCPI_DIR, .num_subcommands = 5,
        .subcommands = (scpi_command*) &(scpi_command[]) {
            {.name="FREQuency", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL},
            {.name="TIMEout", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL},
            {.name="STARt", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL},
            {.name="STOP", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL},
            {.name="STATus", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL},

        }
    },

};

static struct scpi_command scpi_specials[] = {
    {.name="IDN", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_idn, .subcommands = NULL},
    {.name="OPC", .scpi_handler=scpi_handler_nyi, .scpi_query=scpi_query_nyi, .subcommands = NULL},
    {.name="CLR", .scpi_handler=scpi_clear, .scpi_query=NULL, .subcommands = NULL}
};



#endif //SCPI_GPA_SCPI_H
