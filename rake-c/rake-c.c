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


void send_quote_req(int sock)
{   
    // CONVERT TO HOST TO NETWORK BYTE ORDER (BIG EDIAN)
    // ALWAYS CONVERTS INTS TO 4 BYTES LONG
    int cmd  = htonl( CMD_QUOTE_REQUEST );

    printf("SENDING: %i\n", cmd);
    // SEND THE REQ
    send(sock, &cmd, sizeof(cmd), 0);
    printf("SENDING FOR QUOTE\n");

    // BUFFER FOR THE CMD FROM SERVER - SHOULD BE CMD_QUOTE_REPLY
    // WE WILL BE DOING THIS PART ALOT A FUNCTION WOULD BE HELPFUL
    // SEE PYTHON VERSION FOR MORE DETS OR TALK TO TOM
    char buffer[32];
    int byte_count = 0; // SHOULD BE 4
    byte_count = recv(sock, buffer, sizeof(buffer), 0);

    if(byte_count == 0){
        printf("WE DIDNT RECV ANYTHING");
        exit(EXIT_FAILURE);
    }

    printf("RECV: %i\n", atoi(buffer));

    // CHECK WE RECV THE CORRECT ACK
    if(atoi(buffer) != CMD_QUOTE_REPLY)
    {
        printf("SOMETHING WENT WRONG\n");
        exit(EXIT_FAILURE);
    }

    // RECV QUOTE AGAIN QUOTE IS A INT SO IT SHOULD BE 4 BYTES LONG ASWELL
    byte_count = 0; // SHOULD BE 4
    byte_count = recv(sock, buffer, sizeof(buffer), 0);

    int quote = atoi(buffer);

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
    serv_addr.sin_port   = htons(SERVER_PORT);

    printf("CONNECTING TO (%s : %i)\n", host, port);

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
