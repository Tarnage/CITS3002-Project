#ifndef RAKE_C_H
#define RAKE_C_H

#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <netdb.h>
#include <arpa/inet.h>

#include "parse_c.h"

typedef enum _cmd{
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
} CMD;

#define MAX_BYTES_SIGMA 4

#endif