#ifndef CLIENT_SOCKET_H
#define CLIENT_SOCKET_H
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <time.h>

#include "logger_c.h"

#define FILE_FORMAT  "%d-%m-%Y.log"
#define SERVER_PORT  50006
#define SERVER_HOST  "192.168.1.111"
#define MAX_BYTES    1024

extern int client_socket (char *, int);


#endif