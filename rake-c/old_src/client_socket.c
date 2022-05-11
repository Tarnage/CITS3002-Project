#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <netdb.h>
#include <arpa/inet.h>

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
#define MAX_BYTES    1024


int create_conn(char *host, int port)
{   
    int sock = -1;
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port   = htons(SERVER_PORT);

    // CHECK SOCKET CREATION
    if( (sock = socket(AF_INET, SOCK_STREAM, 0)) < 0 ){
        printf("\nSocket creation error\n");
        exit(EXIT_FAILURE);
    }

    // CONVERT IPv4 and IPv6 ADDRESSES FROM STRING TO BINARY
    if( inet_pton(AF_INET, SERVER_HOST, &serv_addr.sin_addr) <= 0 ) {
        printf("\nInvaild address or address not supported\n");
        exit(EXIT_FAILURE);
    }

    // CHECK CONNECTION
    if( connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0 ) {
        printf("\nConnection Failed\n");
        exit(EXIT_FAILURE);
    }

    return sock;
}

void handle_conn() {
    
    exit(EXIT_SUCCESS);
}

/*
int main()
{   
    int sd = -1;
    sd = create_conn(SERVER_HOST, SERVER_PORT);

    return 0;
} */