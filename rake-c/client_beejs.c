#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

#ifndef _POSIX_C_SOURCE 200112L
#define _POSIX_C_SOURCE 200112L
#endif


// DEFAULT VALUES
#define SERVER_PORT  "6327"
#define SERVER_HOST  "localhost"

// MACRO TO CHECK AND ASSIGN 
#define CHECK(e) if( (e) != 0 ){printf("Error occured while trying to connect\n");}

void handle_conn()
{   
    
    // STATUS USED FOR ERROR CHECKING
    int status = -1;
    int sd = -1;
    struct addrinfo hints;
    // LINKED LIST OF RESULTS
    struct addrinfo *res;

    // SET STRUCT TO ZEROS
    memset(&hints, 0, sizeof(hints));
    // SETS FAMILY TO IPv4, AF_UNSPEC FOR BOTH IPv4 AND IPv6
    hints.ai_family = AF_INET; 
    // TCP STREAM SOCKET
    hints.ai_socktype = SOCK_STREAM;

    // GET READY TO CONNECT
    getaddrinfo(SERVER_HOST, SERVER_PORT, &hints, &res);
    
    sd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);

    connect(sd, res->ai_addr, res->ai_addrlen);
    
}

int main(int argc, char const *argv[])
{
    handle_conn();
    return 0;
}
