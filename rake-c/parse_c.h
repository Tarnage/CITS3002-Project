#ifndef PARSE_C
#define PARSE_C

// LIBRARIES
#include "rake-c.h"
#include "structures.h" 
#include "strsplit.h"

#define MAX_LINE_LENGTH 128

// GLOBALS
int num_hosts;
int num_actions;
int num_sets;



//-------------------------------------------------------------------------------------
extern  void    file_process(char*, ACTION_SET*, HOST*);
extern  char    *trim_whitespace(char *);
extern  void    print_action_sets(ACTION_SET *);
extern  void    print_hosts(HOST*);
#endif