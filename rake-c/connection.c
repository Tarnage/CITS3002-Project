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

void create_socket(char *host, int port)
{
    int sock_desc = 0;

    struct sockaddr_in server_addr;

    sock_desc = socket(AF_INET, SOCK_STREAM, 0);

    // CHECK IF SOCKET WAS MADE SUCCESSFULLY
    if(sock_desc == -1)
    {
        perror("Error:" );
        exit(EXIT_FAILURE);
    }
    else
    {
        printf("SOCKET CREATED\n");
    }
}