#ifndef PARSE_C
#define PARSE_C

#if defined(__linux__)
extern  char    *strdup(const char *str);
#endif

#define MAX_LINE_LENGTH 256
#define MAX_ACTIONS     256
#define MAX_SETS        256
#define MAX_HOSTS       256

// LIBRARIES
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

#include "strsplit.h"
#include "structures.h"

//-----------------------------------GLOBALS----------------------------------------------

int num_actions;

int default_port;
//-----------------------------------MACROS----------------------------------------------

#define ACTION_DATA(i,j)     action_set[i].actions[j]

//---------------------------------DECLARATIONS-----------------------------------------

extern  void    file_process(char*, ACTION_SET*, int*, HOST*, int*);
extern  char    *trim_whitespace(char *);
extern  void    print_action_sets(ACTION_SET *, int);
extern  void    print_hosts(HOST*, int);
extern  void    print_array_words(char **, int);
#endif
