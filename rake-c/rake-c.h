#ifndef RAKE_C_H
#define RAKE_C_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "logger_c.h"
#include "parse_c.h"
#include "structures.h"
#include "execution.h" 
#include "connection.h"

#define ACTION_DATA(i,j)     action_set[i].actions[j]

enum command 
{
    CMD_ECHO,
    CMD_ECHOREPLY,
    CMD_QUOTE_REQUEST,
    CMD_QUOTE_REPLY,
    CMD_SEND_REQUIREMENTS,
    CMD_BIN_FILE,
    CMD_SEND_FILE,
    CMD_SEND_SIZE,
    CMD_SEND_NAME,
    CMD_EXECUTE_REQ,
    CMD_EXECUTE,
    CMD_RETURN_STATUS,
    CMD_RETURN_STDOUT,
    CMD_RETURN_STDERR,
    CMD_RETURN_FILE,
    CMD_ACK
};

ACTION_SET action_set[MAX_ACTIONS];
HOST       hosts[MAX_HOSTS];


#endif