//
// Created by atmelfan on 2017-02-06.
//

#include "gpa_scpi.h"
#include <string.h>
#include <ctype.h>

//NAVIGATE
//nav
char* def = "NULL";

const char* skip_ws(const char* s){
    while(isspace(*s)) s++;
    return s;
}

const char* compare_command(const char* str, const char* command) {
    while(*command){
        char c = *command;
        char s = (char)tolower(*str);
        if(!isalnum(s)){
            return islower(c) ? str : NULL;//s has ended, return true if command is lowercase(optional) or null
        }
        if(s != tolower(c)){
            return NULL;
        }
        //scpi_print(command);
        command++;
        str++;
    }
    return (isspace(*str) || *str == ':' || *str == '?' || *str == ';' || *str == '\0'|| *str == '\r') ? str : NULL;
}



void scpi_execute_F(const char *command, struct scpi_command* commands, int N) {
    command = skip_ws(command);
    struct scpi_command* coms = commands;
    struct scpi_command* next = commands;
    int nextN = N;

    if(*command == '\0') return;

    if(*command == ':'){
        command++;
        scpi_execute(command);
        return;
    }

    if(*command == '*'){
        command++;
        coms = scpi_specials;
        N = sizeof(scpi_specials)/sizeof(scpi_command);
    }

    for (int i = 0; i < N; ++i) {
        const char* s = compare_command(command, coms[i].name);
        //Not a match! Try next.
        if(s == NULL){
            continue;
        }
        //
        if(*s == ':'){
            s++;
            if(coms[i].subcommands != NULL){
                scpi_execute_F(s, coms[i].subcommands, coms[i].num_subcommands);
            }else{
                scpi_println("[SCPI] No subcommands!");
            }

        }else if(*s == '?'){
            s++;
            skip_ws(s);
            if(coms[i].scpi_query != NULL){
                s = coms[i].scpi_query(s);
            }else{
                scpi_println("[SCPI] Not queryable!");
            }
            if(s != NULL){
                s++;
                scpi_execute_F(s, next, nextN);
            }
        }else{
            skip_ws(s);
            if(coms[i].scpi_handler != NULL){
                s = coms[i].scpi_handler(s);
            }else{
                scpi_println("[SCPI] Not callable!");
            }
            if(s != NULL){
                s++;
                scpi_execute_F(s, next, nextN);
            }
        }
        return;

    }
    //No commands matched.
    scpi_println("[SCPI] Command does not exist!");
}

void scpi_execute(const char* command){
    scpi_execute_F(command, scpi_commands, sizeof(scpi_commands)/sizeof(scpi_command));
}

const char* scpi_nop(const char *command) {
    return strchr(command, ';');
}

const char *scpi_query_nyi(const char *command) {
    scpi_println("QUERY NOT YET IMPLEMENTED!");
    return scpi_nop(command);
}

const char *scpi_handler_nyi(const char *command) {
    scpi_println("COMMAND NOT YET IMPLEMENTED!");
    return scpi_nop(command);
}

const char *scpi_idn(const char *command) {
    scpi_println(SCPI_IDN);
    return scpi_nop(command);
}

const char *scpi_clear(const char *command) {
    scpi_println("\033[2J");
    return scpi_nop(command);;
}

void scpi_println(const char *s) {
    scpi_print(s);
    scpi_print("\r\n");

}
