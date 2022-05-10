#include "connection.h"

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
}