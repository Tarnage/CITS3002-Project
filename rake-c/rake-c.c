#include "rake-c.h"

#ifndef __APPLE__
// NOT STANDARD LIB CAN INSTALL WITH sudo apt -y install libexplain-dev
#include <libexplain/connect.h>
#endif

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
#define MAX_BYTES    1024


//--------------------GLOBALS-------------------
int n_sock_list = 0;
NODE *sock_cost_list;


// FILLS STRUCTS WITH RAKEFILE CONTENTS
void init_actions(char *file_name, ACTION_SET *actions, HOST *hosts)
{
    file_process(file_name, actions, hosts);
    // n_hosts = num_hosts;
    // n_actions = num_sets;
}


// HELPER TO CHECK THAT WE RECEIVE BYTES
void print_bytes(char *buffer)
{   
    printf("BYTES ");
    for (int i = 0; i < 4; i++)
    {
        printf("%02X ", buffer[i]);
    }
    printf("\n");   
}


// USED TO RECVEIVE INTEGERS SUCH AS ENUMS FILE SIZES AND COST REQ
// SINCE ALL INTS WILL BE 4 BYTES LONG
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


// HELPER TO ADD COST TO SOCK LIST 
void add_quote(int sock, int quote)
{
    NODE *tmp = sock_cost_list;
    printf("APPENDING CURRENT QUOTE: %i\n", quote);
    while(tmp->sock != sock) ++tmp;
    tmp->cost = quote;
}


// SEND REQ AND RECEIVE QUOTES
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

    add_quote(sock, quote);
}


// MAIN CONNECTION HANDLER
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


// CREATES SOCKET DESCRIPTORS
int create_conn(char *host, int port)
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
#ifndef __APPLE__
        fprintf(stderr, "%s\n", explain_connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) );
#else
		printf("\nConnection failed!!\n");
#endif
        exit(EXIT_FAILURE);
    }

    printf("SOCKET CREATION SUCCESSFUL\n");

    return sock;
}


// HELPER TO FILL OUT SOCK LIST WITH CONNECTIONS
void get_all_conn(NODE *list, HOST *hosts)
{   
    while(1)
    {   
        if (hosts->name == NULL)
        {
            break;
        }
        
        list->next = (NODE*)malloc(sizeof(NODE));

        list->ip = hosts->name;
        list->port = hosts->port;
        list->sock = create_conn(hosts->name, hosts->port);
        
        ++n_sock_list;
        ++list;
        ++hosts;
    }
    
    list->next = NULL; 
}


// FOR TESTING PRINT THE CURRENT SOCK LIST
void print_sock_list(NODE *list)
{   
    int i = 0;
    printf("CURRENT SOCKET LIST\n");
    while(i != n_sock_list)
    {
        int sock = list->sock;
        char *ip = list->ip;
        int port = list->port;
        int cost = list->cost;

        //printf("%i: (%s:%i)\n", sock, ip, port);
        printf("%i: (%s:%i) %i\n", sock, ip, port, cost);

        ++list;
        ++i;
    }
}


// HELPER TO LOOP OVER ALL SOCKETS IN THE LIST AND GET THE COST
void get_all_costs(NODE *list)
{
    int i = 0;
    printf("GETTING COST FOR ALL CONNECTIONS\n");
    while(i != n_sock_list)
    {
        handle_conn(list->sock, CMD_QUOTE_REQUEST);
        ++list;
        ++i;
    }
}


int main (int argc, char *argv[])
{   
    char *file_name;
    if(argc != 2)
    {
        file_name = "Rakefile";
    }
    else
    {
        file_name = argv[1];
    }
    
    HOST hosts[MAX_HOSTS];
    ACTION_SET action_set[MAX_ACTIONS];
    // int host_count = 0;
    // int action_count = 0;
    sock_cost_list = (NODE*)malloc(sizeof(NODE));

    init_actions(file_name, action_set, hosts);

    //print_hosts(hosts, host_count);
    //print_action_sets(action_set, action_count);

#define COMMAND(i,j)     action_set[i].actions[j]
    for (size_t i = 0; i < num_sets; i++)
    {   
        size_t action_count = action_set[i].action_totals;
        for (size_t j = 0; j < action_count; j++)
        {   
            // CHECK IF ITS A REMOTE COMMAND
            if(COMMAND(i,j).is_remote != 1)
            {   
                //TODO: HANDLE LOCAL EXECUTIONS
                continue;
            }
            else
            {   
                // TODO: GET THE LOWEST COST
                get_all_conn(sock_cost_list, hosts);

                get_all_costs(sock_cost_list);
                
                print_sock_list(sock_cost_list);

                if(COMMAND(i,j).req_count > 0)
                {
                    // TODO: HANDLE FILE TRANSFERS
                }
                else
                {
                    // TODO: NO FILE REQS JUST RUN SEND THE COMMAND
                }
            }

        }
        
    }

    // perform_actions(action_set);

    return 0; 
}
