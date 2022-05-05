#ifndef RAKE_C_H
#define RAKE_C_H
// LIBRARIES
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "strsplit.c"

// STRUCTURES
typedef struct _action
{
    char *command; 
    int is_remote;
    char **requirements; 
} ACTION;

typedef struct _host
{
    char *name;
    int port;
} HOST;

// VARIABLES

// AN ACTION SET IS AN ARRAY OF ACTIONS PER SET
ACTION  **action_set; 
// AN ARRAY OF HOSTS
HOST    *hosts;
// THE NUMBER OF HOSTS
int num_hosts; 
// THE NUMBER OF ACTION SETS
int num_sets;
// A COUNTER FOR ACTIONS FOR EACH ACTION SET
// THIS NUMBER WILL BE RESET TO ZERO EVERY TIME A NEW ACTION SET IS INCOMING
int num_actions; 


// FUNCTIONS
extern  void    file_process(char *);

extern  void    remove_str(char*, char, char*);

extern  void    perform_actions();

#endif