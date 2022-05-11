#include "rake-c.h"

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
#define MAX_BYTES    1024


void init_actions(char *file_name, ACTION_SET *actions, HOST *hosts)
{
    file_process(file_name, actions, hosts);
    // n_hosts = num_hosts;
    // n_actions = num_sets;
}


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

    printf("Socket Creation Successful");
    return sock;
}

void handle_conn() {
    
    exit(EXIT_SUCCESS);
}



int main (int argc, char *argv[])
{   
    HOST hosts[MAX_HOSTS];
    ACTION_SET action_set[MAX_ACTIONS];
    // int host_count = 0;
    // int action_count = 0;

    char *file_name;
    if(argc != 2)
    {
        file_name = "Rakefile";
    }
    else
    {
        file_name = argv[1];
    }
    
    init_actions(file_name, action_set, hosts);

    //print_hosts(hosts, host_count);
    // print_action_sets(action_set, action_count);

    printf("%i\n", num_hosts);
    for(int i = 0; i < num_hosts; i++)
    {   
        int sock = -1;
        sock = create_conn(hosts[i].name, hosts[i].port);

        printf("%d\n", sock);
    }

    // perform_actions(action_set);

    return 0; 
}
