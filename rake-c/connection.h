#ifndef CONNECT_H
#define CONNECT_H
#include "rake-c.h"
#include "structures.h"
#include "parse_c.h"
// #include "client_socket.h"
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#define SERVER_PORT 50009
#define SERVER_HOST "127.0.0.1"



extern void create_socket(char *, int);

#endif