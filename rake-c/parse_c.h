#ifndef PARSE_C
#define PARSE_C

// LIBRARIES
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "strsplit.c"

#define MAX_LINE_LENGTH 128
#define MAX_ACTIONS     32
#define MAX_SETS        16
#define MAX_HOSTS       32

// STRUCTURES
typedef struct _action
{
    char *command; 
    int is_remote;
    int req_count;
    char **requirements; 
} ACTION;

typedef struct _host
{
    char *name;
    int port;
} HOST;

typedef struct _actionset
{
    ACTION actions[MAX_ACTIONS];
    int action_totals;
} ACTION_SET;

//-------------------------------------------------------------------------------------
extern  void    file_process(char*, ACTION_SET*, HOST*);
#endif