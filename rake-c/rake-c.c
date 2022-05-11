#include "rake-c.h"

// NOT STANDARD LIB CAN INSTALL WITH sudo apt -y install libexplain-dev
#include <libexplain/connect.h>

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
#define MAX_BYTES    1024


void init_actions(char *file_name, ACTION_SET *actions, HOST *hosts)
{
    file_process(file_name, actions, hosts);
    // n_hosts = num_hosts;
    // n_actions = num_sets;
}


void print_bytes(char *buffer)
{   
    printf("BYTES ");
    for (int i = 0; i < 4; i++)
    {
        printf("%02X ", buffer[i]);
    }
    printf("\n");   
}


int recv_byte_int(int sock)
{
    uint32_t result = 0;
    char buffer[MAX_BYTES_SIGMA];
    bzero(buffer, MAX_BYTES_SIGMA);
    int byte_count = 0; // SHOULD BE 4
    byte_count = recv(sock, buffer, sizeof(buffer), 0);

    if(byte_count == 0){
        printf("WE DIDNT RECV ANYTHING");
        exit(EXIT_FAILURE);
    }

    memcpy(&result, buffer, MAX_BYTES_SIGMA);

    return ntohl(result);
}


void send_quote_req(int sock)
{   
    // CONVERT TO HOST TO NETWORK BYTE ORDER (BIG EDIAN)
    // ALWAYS CONVERTS INTS TO 4 BYTES LONG
    int cmd  = htonl( CMD_QUOTE_REQUEST );

    // SEND THE REQ
    send(sock, &cmd, sizeof(cmd), 0);
    printf("REQUESTING FOR QUOTE\n");

    int recv_cmd = recv_byte_int(sock);

    // CHECK WE RECV THE CORRECT ACK
    if(recv_cmd != CMD_QUOTE_REPLY)
    {
        printf("SOMETHING WENT WRONG\n");
        exit(EXIT_FAILURE);
    }

    // RECV QUOTE AGAIN QUOTE IS A INT SO IT SHOULD BE 4 BYTES LONG ASWELL

    int quote = recv_byte_int(sock);

    printf("QUOTE RECEIVED: %i\n", quote);
}


void handle_conn(int sock, CMD ack_type) 
{
    // WHILE THERE IS A SOCKING WAITING TO SEND OR RECV, QUEUE >=1
    int queue = 1;

    while (queue)
    {   
        switch (ack_type)
        {
        case CMD_QUOTE_REQUEST:
            send_quote_req(sock);
            close(sock);
            queue = 0;
            break;
        
        default:
            break;
        }
    }
    
}


int create_conn(char *host, int port, CMD ack_type)
{   
    int sock = -1;
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port   = htons(port);


    printf("CONNECTING TO (%s:%i)\n", host, port);

    // CHECK SOCKET CREATION
    if( (sock = socket(AF_INET, SOCK_STREAM, 0)) < 0 ){
        printf("\nSocket creation error\n");
        exit(EXIT_FAILURE);
    }

    // CONVERT IPv4 and IPv6 ADDRESSES FROM STRING TO BINARY
    if( inet_pton(AF_INET, host, &serv_addr.sin_addr) <= 0 ) {
        printf("\nInvaild address or address not supported\n");
        exit(EXIT_FAILURE);
    }

    // CHECK CONNECTION
    int status = -1;
    if( (status = connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr))) < 0 ) {
        fprintf(stderr, "%s\n", explain_connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) );
        exit(EXIT_FAILURE);
    }

    printf("Socket Creation Successful\n");

    // PASS TO A FUNCTION TO HANDLE CONNECTIONS
    handle_conn(sock, ack_type);
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

    for(int i = 0; i < num_hosts; i++)
    {     
        create_conn(hosts[i].name, hosts[i].port, CMD_QUOTE_REQUEST);
    }

    // perform_actions(action_set);

    return 0; 
}
