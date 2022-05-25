#include "rake-c.h"
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
#define LOCAL_HOST   "127.0.0.1"
#define MAX_BYTES    1024
#define MAX_SOCKETS  FD_SETSIZE
// #define USE_FIND_FILE

//--------------------GLOBALS-------------------


// FILLS STRUCTS WITH RAKEFILE CONTENTS
void init_actions(char *file_name, ACTION_SET *actions, int *n_sets, HOST *hosts, int *n_hosts)
{
    file_process(file_name, actions, n_sets, hosts, n_hosts);
}


// HELPER TO CHECK THAT WE RECEIVE BYTES
void print_bytes(char *buffer)
{   
    //printf("BYTES ");
    for (int i = 0; i < 4; i++)
    {
        printf("%02X ", buffer[i]);
    }
    printf("\n");   
}


// FOR TESTING PRINT THE CURRENT SOCK LIST
void print_sock_list(NODE *list)
{   
    NODE *temp = list;
    printf("CURRENT SOCKET LIST\n");
    while(temp->next != NULL)
    {
        int sock = temp->sock;
        char *host = temp->ip;
        int port = temp->port;
        int cost = temp->cost;

        //printf("%i: (%s:%i)\n", sock, ip, port);
        printf("%i: (%s:%i) %i\n", sock, host, port, cost);

        temp = temp->next;
    }
}


// CONVERT TO HOST TO NETWORK BYTE ORDER (BIG EDIAN)
// ALWAYS CONVERTS INTS TO 4 BYTES LONG
void send_byte_int(int sd, CMD preamble)
{
    int cmd  = htonl( preamble );
    //printf("SENDING INT ----> %d\n", preamble);
    send(sd, &cmd, sizeof(cmd), 0);
}


// USED TO RECVEIVE INTEGERS SUCH AS ENUMS FILE SIZES AND COST REQ
// SINCE ALL INTS WILL BE 4 BYTES LONG
int recv_byte_int(int sock)
{
    char buffer[MAX_BYTES_SIGMA];
    bzero(buffer, MAX_BYTES_SIGMA);
    int byte_count = 0; // SHOULD BE 4
    
    byte_count = recv(sock, buffer, sizeof(buffer), 0);
    if(byte_count < 4){
        printf("INTEGER NOT RECEIVED\n");
        exit(EXIT_FAILURE);
    }
	uint32_t result = 0;
    memcpy(&result, buffer, MAX_BYTES_SIGMA);

    return ntohl(result);
}

// SENDS THE LEN OF THE STR FOLLOWED BY THE STR
void send_string(int sd, char *payload)
{
	int size = strlen(payload);
	send_byte_int(sd, size);
	send(sd, payload, size, 0);
}


// SEND TEXT FILE TO SERVER
void send_file(int sd, char *filename)
{    
    char *last = strrchr(filename, '/');
    char *real_file_name;
    if (last != NULL) real_file_name = strdup(last+1);
    else real_file_name = strdup(filename);

    if(strstr(filename, ".") != NULL)
    {   
        if(strstr(filename, ".o") != NULL) send_byte_int(sd, CMD_BIN_FILE);   
        else send_byte_int(sd, CMD_SEND_FILE);
    }
    else send_byte_int(sd, CMD_BIN_FILE);
    
    //printf("SENDING FILE NAME ----> %s\n", real_file_name);

    send_string(sd, real_file_name);
    FILE *fp = fopen(filename, "rb");
    if (fp == NULL) exit(EXIT_FAILURE);
    else 
    {
        struct stat st;
        stat(filename, &st);
        int size = st.st_size;
        char buffer[size]; 
        fread(buffer, size, 1, fp);
        send_byte_int(sd, size);
        send(sd, buffer, size, 0);
    }

    fclose(fp);
}


// RECV THE SIZE OF INCOMING PAYLOAD AND THEN RECV THE PAYLOAD
void recv_string(int sock, char *string, int size)
{
    char buffer[size]; 
    int byte_count = 0; 
    byte_count = recv(sock, buffer, sizeof(buffer), 0);
    if(byte_count == 0)
    {
        printf("WE DIDNT RECV ANYTHING\n");
        exit(EXIT_FAILURE);
    }
    memcpy(string, buffer, byte_count);
    string[byte_count] = '\0';
}


/*
    FUNCTION: recv_bin_file
    INPUT: sock (Integer)
    OUTPUT: N/A

    ASSERTION: RECEIVE A BINARY FILE FROM THE SERVER
*/ 
void recv_bin_file(int sock)
{
    int str_size = recv_byte_int(sock);
    char filename[str_size]; 
    recv_string(sock, filename, str_size);
    int file_size = recv_byte_int(sock);

    FILE *fp = fopen(filename, "wb");
    if (fp == NULL)
    {
        printf("PROBLEM: FILE DOES NOT EXIST\n");
        exit(EXIT_FAILURE);
    }

    unsigned char buffer[file_size];
    int byte_count = recv(sock, buffer, sizeof(buffer), 0);
    if(byte_count == 0)
    {
        printf("FILE CONTENTS NOT RECEIVED\n");
        exit(EXIT_FAILURE);
    }

    fwrite(buffer, file_size, 1, fp);
    fclose(fp);
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
		printf("\nConnection failed!!\n");
        exit(EXIT_FAILURE);
    }

    return sock;
}


// CREATE THE LOCAL HOST NODE 
void create_local_node(NODE *local)
{   
    create_node(local, LOCAL_HOST, default_port);
}

// FIND THE LOWEST COST HOST/PORT PAIR IN THE LIST 
char *get_lowest_cost(NODE *list, int *port)
{   
    int curr = INT_MAX;
    char *temp_ip;
    int temp_port = -1;
    
    NODE *temp = list;
    while(temp != NULL)
    {   
        if(temp->cost < curr)
        {   
            curr = temp->cost;
            temp_ip = strdup(temp->ip);
            temp_port = temp->port;
        }
        temp = temp->next;
    }
    *port = temp_port;
    
    free_list(list);
    return temp_ip;
}


// HELPER TO FIND WHAT REQ THE SOCKET IS DOING
// i.e. ARE THEY JUST ASKING FOR A COST REQUEST OR ARE THEY SENDING A FILE
CMD get_curr_req(NODE *local, NODE *conn_list, NODE *quote_team, int sd) 
{   
    CMD result = -1;
    if(local->sock == sd) return local->curr_req;

    NODE *temp = quote_team;
    while(temp != NULL)
    {   
        if(temp->sock == sd) return temp->curr_req;
        temp = temp->next;
    }
    
    temp = conn_list;
    while(temp != NULL)
    {
        if(temp->sock == sd) return temp->curr_req;
        temp = temp->next;
    }

    return result;
}


// WRAPPER FUNCTION FOR SENDING COST REQUEST 
void send_cost_req(int sd)
{   
    //printf("SENDING COST REQUEST ---->\n");
    send_byte_int(sd, CMD_QUOTE_REQUEST);
}


// RETURNS NODE ASSOCIATED WITH sd
NODE *get_node(NODE *local, NODE* conn_list, int sd)
{
    if(local->sock == sd) return local;

    NODE *temp = conn_list;
    while(temp != NULL)
    {
        if(temp->sock == sd) return temp;
        temp = temp->next;
    }
    return NULL;
}


// HELPER SEND CMD ACK FOLLOWED BY THE CMD
void send_cmd(int sd, char *cmd)
{   
    //printf("SENDING COMMAND ----> %s\n", cmd);
    send_byte_int(sd, CMD_EXECUTE);
    send_string(sd, cmd);
}


// LOOPS OVER ALL AVAILABLE CONNECTIONS AND SENDS THEM OUT FOR QUOTES
void create_quote_team(HOST *hosts, int n_hosts ,NODE *new_list, fd_set outputs)
{   
    NODE *temp = NULL;
    for (size_t i = 0; i < n_hosts; i++)
    {   
        int sock = create_conn(hosts[i].name, hosts[i].port);
        NODE *new_node = (NODE*)malloc(sizeof(NODE));
        create_node(new_node, hosts[i].name, hosts[i].port);
        FD_SET(sock, &outputs);
        new_node->sock = sock;
        new_node->curr_req = CMD_QUOTE_REQUEST;
        if(temp == NULL) temp = new_node;
        else append_new_node(temp, new_node); 
    }
}


// MAIN CONNECTION HANDLER
void handle_conn(HOST *hosts, int n_hosts, ACTION* actions, int action_totals) 
{
    // SOCKETS TO READ FROM
    fd_set input_sockets, read_ready;
    FD_ZERO(&input_sockets);

    // SOCKETS TO WRITE TO
    fd_set output_sockets, write_ready;
    FD_ZERO(&output_sockets);

    // LIST OF SOCKETS MAKING A REQUEST
    NODE *quote_list = NULL;
    // CURRENT QUOTE INDEX
    int curr_quote_req = 0;
    // HOW MANY HAVE QUOTES HAVE COME BACK
    int quote_recv = 0;

    // LIST OF CONNECTIONS EXECUTING ACTIONS
    NODE *conn_list = NULL;

    // OUR LOCAL SERVER
    NODE *local_host = (NODE*)malloc(sizeof(NODE));
    int local_socket = -1;
    create_local_node(local_host);
    
	// NUMBER OF EXECUTED ACTIONS
    int actions_executed = 0;

	// THE NEXT ACTION
    int next_action = 0;

    // REMAINING ACTIONS
    int remaining_actions = action_totals;
    
    while (actions_executed < remaining_actions)
    {   
        if(next_action < remaining_actions)
        {
            // LOCAL 
            if( !actions[next_action].is_remote && local_socket < 0)
            {
                int socket_desc = create_conn(local_host->ip, local_host->port);
                FD_SET(socket_desc, &output_sockets);

                local_host->sock = socket_desc;
                local_socket = socket_desc;
                local_host->curr_req = CMD_SEND_FILE;
                local_host->actions = &actions[next_action];
                
                ++next_action;
                ++curr_quote_req;
            }

            if( (curr_quote_req == next_action) && (actions[next_action].is_remote) && (quote_recv == 0) )
            {
                printf("REMOTE ACTION - BUILDING QUOTE FD_SET...\n");
                // BUILDING THE FD_SET
                for (size_t i = 0; i < n_hosts; i++)
                {   
                    int sock = create_conn(hosts[i].name, hosts[i].port);
                    FD_SET(sock, &output_sockets);

                    // CREATE NODE FOR EACH COST REQUEST sock
                    NODE *new_node = (NODE*)malloc(sizeof(NODE));
                    create_node(new_node, hosts[i].name, hosts[i].port);
                    new_node->sock = sock;
                    new_node->curr_req = CMD_QUOTE_REQUEST;

                    // APPEND IT TO THE quote_list
                    if(quote_list == NULL) quote_list = new_node;
                    else append_new_node(quote_list, new_node); 
                }
                ++curr_quote_req;
            }
            else if( (next_action < remaining_actions) && (quote_recv == n_hosts) )
            {   
                quote_recv = 0;
                int port = -1;
                char *ip = get_lowest_cost(quote_list, &port);
                int sock = create_conn(ip, port);
                FD_SET(sock, &output_sockets);

                // CREATE NODE FOR sock
                NODE *slave = (NODE*)malloc(sizeof(NODE));
                create_node(slave, ip, port);
                slave->sock = sock;
                slave->curr_req = CMD_SEND_FILE;
                slave->actions = &actions[next_action];

                // APPEND IT TO THE LIST
                if(conn_list == NULL) conn_list = slave;
                else append_new_node(conn_list, slave);
                quote_list = NULL;
                next_action++;
            }
        }

        struct timeval tv;
        tv.tv_sec = 5;
        tv.tv_usec = 0;

        read_ready = input_sockets;
        write_ready = output_sockets;
        int activity = select(FD_SETSIZE+1, &read_ready, &write_ready, NULL, &tv);
        switch (activity)
        {
            case -1:
                perror("select()\n");
                break;
            case 0:
                printf("select() returned 0\n");
                break;
                
            default:
                for (int i = 0; i < FD_SETSIZE; i++)
                {   
                    // CHECK IF SOCK IS READY FOR RECEIVING DATA
                    if (FD_ISSET(i, &read_ready))
                    {   
                        // REMOVE FROM INPUT STATE
                        FD_CLR(i, &input_sockets);

                        int preamble = recv_byte_int(i);
                        // printf("PREAMBLE: %i\n", preamble);
                        if(preamble == CMD_ACK) FD_SET(i, &output_sockets); // JUST RECVEVING AN ACK sockfd CAN GO BACK TO OUTPUT STATE
						
						
                        else if(preamble == CMD_QUOTE_REPLY)
                        {   
							// RECEIVE THE COST OF CONNECTION
                            int cost = recv_byte_int(i);
                            //printf("COST RECEIVED: %i\n", cost);
                            add_cost(quote_list, i, cost);
                            ++quote_recv;
                        }
                        else if(preamble == CMD_RETURN_STATUS)
                        {
							// RECEIVE THE RETURN STATUS
                            int return_code = recv_byte_int(i);
                            if (return_code == 0) preamble = recv_byte_int(i);

                            if(preamble == CMD_RETURN_FILE)
                            {
                                recv_bin_file(i);
                                ++actions_executed;

                                if(i == local_socket) close_local_sock(local_host, &local_socket);
                                else remove_sd(conn_list, i);
                            }
                            
                        }
                        else if (preamble == CMD_RETURN_STDOUT)
                        {
                            int return_code = recv_byte_int(i);
                            printf("RETURN CODE STDOUT: %i\n", return_code);
                            if (return_code > 0 && return_code < 5)
                            {   
                                int size = recv_byte_int(i);
                                char err_msg[size];
                                recv_string(i, err_msg, size);
                                printf("Errno: %i/n", return_code);
                                fputs(err_msg, stdout);

                                if(i == local_socket) close_local_sock(local_host, &local_socket);
                                else remove_sd(conn_list, i);

								exit(EXIT_FAILURE);
                            }
                        }
                        else if (preamble == CMD_RETURN_STDERR)
                        {
                            int return_code = recv_byte_int(i);
                            printf("RETURN CODE STDERR: %i\n", return_code);
                            if (return_code > 5)
                            {
                                int size = recv_byte_int(i);
                                char err_msg[size];
                                recv_string(i, err_msg, size);
                                printf("Errno: %i/n", return_code);
                                fputs(err_msg, stderr);

                                if(i == local_socket) close_local_sock(local_host, &local_socket);
                                else remove_sd(conn_list, i);

								exit(EXIT_FAILURE);
                            }
                        }
                        else if(preamble == CMD_NO_OUTPUT)
                        {   
							// NO OUTPUT RECORDED AFTER THE ACTION
                            int return_code = recv_byte_int(i);
                            printf("RETURN CODE %i\n",return_code);
                            ++actions_executed;

                            if(i == local_socket) close_local_sock(local_host, &local_socket);
                            else remove_sd(conn_list, i);
                        }
                    }

                    // CHECK IF SOCK IS READY TO SEND DATA
                    if (FD_ISSET(i, &write_ready))
                    {   
                        CMD curr_req = get_curr_req(local_host, conn_list, quote_list, i);

                        if(curr_req == CMD_QUOTE_REQUEST) send_cost_req(i);

                        else if(curr_req == CMD_SEND_FILE)
                        {
                            NODE *curr = get_node(local_host, conn_list, i);
                            int file_count = curr->actions->req_count;
                            if (file_count > 1)
                            {   
                                char *next_file_to_send = curr->actions->requirements[file_count-1];
                                send_file(i, next_file_to_send);
                                curr->actions->req_count--;
                            }
                            else
                            {   
                                char *cmd = curr->actions->command;
                                send_cmd(i, cmd);
                            }
                        }

                        // REMOVE FROM OUTPUT STATE TO INPUT STATE
                        FD_CLR(i, &output_sockets);
                        FD_SET(i, &input_sockets);
                    }
                }   
            break;
        }
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
    int num_hosts = 0;
    ACTION_SET action_set[MAX_ACTIONS];
    int num_sets = 0;
    init_actions(file_name, action_set, &num_sets, hosts, &num_hosts);

    for (size_t i = 0; i < num_sets; i++)
    {   
        handle_conn(hosts, num_hosts, action_set[i].actions, action_set[i].action_totals);
    }

    return 0; 
}
