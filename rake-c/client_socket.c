#include "client_socket.h"

int client_socket(char *host, int port) {
    int sock = 0;

    struct sockaddr_in serv_addr;

    char *msg = "Hello from C Client";
    char buffer[MAX_BYTES] = { 0 };
    
    // CHECK SOCKET CREATION
    if( (sock = socket(AF_INET, SOCK_STREAM, 0)) < 0 ){
        printf("\nSocket creation error\n");
        exit(EXIT_FAILURE);
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port   = htons(SERVER_PORT);

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

    send(sock, msg, strlen(msg), 0);
    printf("msg sent!!");
    read(sock, buffer, MAX_BYTES);
    printf("%s\n", buffer);

    close(sock);
    exit(EXIT_SUCCESS);
}

/*
int main()
{   
    time_t now = time(NULL);
    char file[32];
    file[strftime(file, sizeof(file), "./logs/" FILE_FORMAT, localtime(&now))] = '\0';
    FILE *fp;
    fp = fopen(file, "a");
    log_add_fp(fp, LOG_DEBUG);

    log_debug("TEST");

    //client_socket(SERVER_HOST, SERVER_PORT);

    return 0;
} */