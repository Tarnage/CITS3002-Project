#ifndef RAKE_C_H
#define RAKE_C_H
// LIBRARIES
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "strsplit.c"

#define MAX_LINE_LENGTH 80
#define MAX_ACTIONS 20
#define MAX_SETS 10

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

typedef struct _actionset
{
    ACTION *actions;
    int action_totals;
} ACTION_SET;
// VARIABLES

// AN ACTION SET IS AN ARRAY OF ACTIONS PER SET
ACTION_SET  *sets; 
// AN ARRAY OF HOSTS
HOST    *hosts;
// ARRAY OF ACTION TOTALS FOR EACH SET
int     *action_totals;
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