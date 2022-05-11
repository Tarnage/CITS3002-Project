#include "connection.h"

/*
void connect_server(HOST *hosts)
{
    for (int i = 0; i < num_hosts; i++)
    {
        printf("HOST: %s\n", hosts[i].name);
        if (client_socket(hosts[i].name, hosts[i].port) != EXIT_SUCCESS)
        {
            printf("Successful connection");
        }
        else
        {
            exit(EXIT_FAILURE);
        }
    }

    exit(EXIT_SUCCESS);
}*/


// CREATE SOCKET AND CONNECT TO THE PORT
void create_socket(char *host, int port)
{
    // SOCKET DESCRIPTOR
    int sock_desc = 0;

    // SOCKET ADDRESS
    struct sockaddr_in server_addr;


    sock_desc = socket(AF_INET, SOCK_STREAM, 0);

    // CHECK IF SOCKET WAS MADE SUCCESSFULLY
    if(sock_desc < 0)
    {
        perror("Error:" );
        exit(EXIT_FAILURE);
    }
    else
    {
        printf("SOCKET CREATED\n");
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);

    printf("ADDRESS: %s\n", host);

    if (inet_pton(AF_INET, host, &server_addr.sin_addr) <= 0)
    {
        printf("Address not supported\n");
        exit(EXIT_FAILURE);
    }

    printf("Connecting to: %d\n", port);
    if( connect(sock_desc, (struct sockaddr*)&server_addr, sizeof(server_addr) ) < 0)
    {
        printf("CONNECTION FAILED\n");
        exit(EXIT_FAILURE);
    }
    else
    {
        printf("CONNECTION SUCCESSFUL");
    }
}