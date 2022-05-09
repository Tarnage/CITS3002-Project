#ifndef RAKE_C_H
#define RAKE_C_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "logger_c.h"
#include "parse_c.h"
#include "structures.h"
#define ACTION_DATA(i,j)     action_set[i].actions[j]

ACTION_SET action_set[MAX_ACTIONS];
HOST       hosts[MAX_HOSTS];

extern void perform_actions(ACTION_SET *);

#endif