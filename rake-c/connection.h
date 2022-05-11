#ifndef CONNECT_H
#define CONNECT_H
#include "rake-c.h"
#include "structures.h"
#include "parse_c.h"
#include "client_socket.h"

#define SERVER_PORT 50009
#define SERVER_HOST '127.0.0.1'
#define MAX_BYTES 1024

extern void connect_server(HOST *hosts);

#endif