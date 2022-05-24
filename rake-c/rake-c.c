#include "rake-c.h"
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"
#ifndef __APPLE__
// NOT STANDARD LIB CAN INSTALL WITH sudo apt -y install libexplain-dev
#include <libexplain/connect.h>
#endif

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
#define LOCAL_HOST   "127.0.0.1"
#define MAX_BYTES    1024
#define MAX_SOCKETS  FD_SETSIZE
// #define USE_FIND_FILE

//--------------------GLOBALS-------------------
int num_sockets = 0;
NODE *sockets;


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


void send_byte_int(int sd, CMD preamble)
{
    // CONVERT TO HOST TO NETWORK BYTE ORDER (BIG EDIAN)
    // ALWAYS CONVERTS INTS TO 4 BYTES LONG
    int cmd  = htonl( preamble );

    // SEND THE REQ
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
    //printf("BYTE COUNT SHOULD BE 4 == %i\n", byte_count);
    if(byte_count < 4){
        printf("INTEGER NOT RECEIVED\n");
        exit(EXIT_FAILURE);
    }
	uint32_t result = 0;
    memcpy(&result, buffer, MAX_BYTES_SIGMA);

    return ntohl(result);
}


// HELPER TO ADD COST TO SOCK LIST 
void add_quote(int sd, int quote)
{
    NODE *head = sockets;
    while(head != NULL)
    {
        if(head->sock == sd)
        {
            head->cost = quote;
            return;
        }
        head = head->next;
    }
}


void send_string(int sd, char *payload)
{
	int size = strlen(payload);
	send_byte_int(sd, size);
    
	send(sd, payload, size, 0);
    //printf("SENDING STRING ----> %s\n", payload);
    // free(result);
}


// SEND TEXT FILE TO SERVER
void send_file(int sd, char *filename)
{
    //printf("FILE SENDING PROCESS STARTED\n");
    char *last = strrchr(filename, '/');

    char* real_file_name = strdup(last+1);

    if(strstr(filename, ".") != NULL)
    {
        if(strstr(filename, ".o") != NULL)
        {
            send_byte_int(sd, CMD_BIN_FILE);
        }   
        else
        {
            send_byte_int(sd, CMD_SEND_FILE);
        }
    }
    else
    {
        send_byte_int(sd, CMD_BIN_FILE);
    }
    
    //printf("SENDING FILE NAME ----> %s\n", real_file_name);

    send_string(sd, real_file_name);

    FILE *fp = fopen(filename, "rb");

    if (fp == NULL)
    {
        exit(EXIT_FAILURE);
    }
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

    //printf("STRING RECEIVED: %s\n", string);
    // return string; 

}


int check_folder_exists (char *filename)
{
    struct stat st;
    int folder_exists = stat(TEMP_FOLDER, &st);

    return folder_exists;
}


/*
    FUNCTION: recv_bin_file
    INPUT: sock (Integer)
    OUTPUT: N/A

    ASSERTION: RECEIVE A BINARY FILE FROM THE SERVER
*/ 
void recv_bin_file(int sock)
{
    // RECEIVE THE SIZE OF THE FILENAME
    int str_size = recv_byte_int(sock);
    //printf("SIZE OF FILE NAME: %d\n", str_size);
    char filename[str_size]; 

    // RECEIVE THE FILENAME 
    recv_string(sock, filename, str_size);
    //printf("FILE NAME: %s\n", filename);

    // RECEIVE THE SIZE OF THE FILE
    //printf("RECEIVING FILE SIZE\n");
    int file_size = recv_byte_int(sock);
    //printf("FILE SIZE: %d BYTES\n", file_size);

    // TODO: MAKE THIS A CHECK FUNCTION
    // #DEFINE "./tmp/"
    // CAN REUSE THIS CHECK BEFORE EXECUTING LOCAL COMMANDS
    // SINCE WE MIGHT WANT TO RUN THE COMMANDS IN THIS DIR
    if(check_folder_exists(TEMP_FOLDER) == -1)
    {   
        // THERE A MACRO FOR 0777?
        printf("MAKING NEW FOLDER\n");
        mkdir(TEMP_FOLDER, 0777);
    }   

    int new_file_size = strlen(TEMP_FOLDER) + strlen(filename) + 1;
    char dir_for_file[new_file_size];
    strcpy(dir_for_file, TEMP_FOLDER);
    strcat(dir_for_file, filename);
    printf("DIRECTORY FOR FILE: %s\n", dir_for_file);

    
    // OPEN THE FILE
    FILE *fp = fopen(dir_for_file, "wb");
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

    printf("FILE %s RECEIVED SUCCESSFULLY\n", filename);
    // RECEIVE THE FILE'S CONTENTS 
    fwrite(buffer, file_size, 1, fp);

    fclose(fp);
}


// TODO: IMPLEMENT FIND FILE
// SEARCH ENTIRE SYSTEM STORE LOCATION IN PATH AND RETURN SUCCESS = 1 OR FAIL = 0
int find_file(char *filename, char *path)
{
    return 0;
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

    // Set the socket to non-blocking
    // int flags = fcntl(sock, F_GETFL, 0);
    // fcntl(sock, F_SETFL, flags | O_NONBLOCK);
    // sleep(2);

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
void init_nodes(HOST *hosts, int n_hosts)
{    
    NODE *head = sockets->next;
    for(size_t i = 0; i < n_hosts; ++i)
    {   
        head->ip = hosts[i].name;
        head->port = hosts[i].port;
        head->used = false;
        head->cost = INT_MAX;
        head->curr_req = -1;
        head->local = false;
        head->next = (NODE*)malloc(sizeof(NODE));
        head = head->next;
    }
    head = NULL;
}

void create_local_node(NODE *local)
{   
    printf("CREATING NODE\n");
    create_node(local, LOCAL_HOST, default_port);
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


void reset_socket_node(NODE *list)
{   
    list->sock = -1;
    list->cost = INT_MAX;
    list->used = false;
    list->curr_req = -1;
    list->actions = NULL;
}


void get_lowest_cost(NODE *list, char *ip, int *port)
{
    int curr = INT_MAX;
    char *temp_ip;
    int temp_port = -1;
    
    NODE *temp = list;
    while(temp != NULL)
    {
        if(temp->cost < curr)
        {
            temp_ip = strdup(temp->ip);
            temp_port = temp->port;
        }
    }
    ip = temp_ip;
    *port = temp_port;
    
    free_list(list);
}

void make_free(NODE *sockets, int sd)
{
    while(sockets->sock != sd) ++sockets;
    sockets->used = false;
}

// HELPER TO FIND WHAT REQ THE SOCKET IS DOING
// i.e. ARE THEY JUST ASKING FOR A COST REQUEST OR ARE THEY SENDING A FILE
CMD get_curr_req(NODE *local, NODE *conn_list, NODE *quote_team, int sd) 
{   
    CMD result = -1;

    if(local->sock == sd)
    {
        return local->curr_req;
    }
    
    NODE *temp = quote_team;
    while(temp != NULL)
    {
        if(temp->sock == sd)
        {
            return temp->curr_req;
        }
        printf("HAPPENS HERE\n");
        temp = temp->next;
        
    }
    
    temp = conn_list;
    while(temp != NULL)
    {
        if(temp->sock == sd)
        {
            return temp->curr_req;
        }
        temp = temp->next;
    }

    free(temp);
    return result;
}


void close_all_sockets()
{
    NODE *head = sockets;
    do
    {
        close(head->sock);
        head = head->next;
    } while (head != NULL);

    exit(EXIT_FAILURE);
    
}


// HELPER TO CHANGE SOCKET STATE 
// MIGHT NOT NEED
void change_state(int sd, CMD state) 
{   
    NODE *head = sockets;
    while(head != NULL)
    {
        if(head->sock == sd)
        {
            head->curr_req = state;
            return;
        }
        head = head->next;
    }
}


void recv_cost_reply(int sd)
{
    int cost = recv_byte_int(sd);
    //printf("COST RECEIVED: %d\n", cost);
    add_quote(sd, cost);
}


void send_cost_req(int sd)
{   
    //printf("SENDING COST REQUEST ---->\n");
    send_byte_int(sd, CMD_QUOTE_REQUEST);
    // SET THE NODE TO EXPECT A REPLY
    change_state(sd, CMD_QUOTE_REPLY);
}


NODE *get_node(NODE *local, NODE* conn_list, int sd)
{
    if(local->sock == sd)
    {
        return local;
    }

    NODE *temp = conn_list;
    while(temp != NULL)
    {
        if(temp->sock == sd)
        {
            return temp;
        }
        temp = temp->next;
    }
    return NULL;
}


void send_cmd(int sd, char *cmd)
{   
    //printf("SENDING COMMAND ----> %s\n", cmd);
    // TODO send command to server to execute
    send_byte_int(sd, CMD_EXECUTE);
    send_string(sd, cmd);
}


void create_quote_team(HOST *hosts, int n_hosts ,NODE *new_list, fd_set outputs)
{   
    NODE *temp = NULL;
    for (size_t i = 0; i < n_hosts; i++)
    {   
        int sock = create_conn(hosts[i].name, hosts[i].port);
        printf("%i\n", sock);
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
    fd_set input_sockets;
    FD_ZERO(&input_sockets);

    // SOCKETS TO WRITE TO
    fd_set output_sockets;
    FD_ZERO(&output_sockets);

    // LIST OF SOCKETS MAKING A REQUEST
    NODE *quote_list;
    // CURRENT QUOTE INDEX
    int curr_quote_req = 0;
    // HOW MANY HAVE QUOTES HAVE COME BACK
    int quote_recv = 0;

    // LIST OF CONNECTIONS EXECUTING ACTIONS
    NODE *conn_list;

    // OUR LOCAL SERVER
    NODE *local_host = (NODE*)malloc(sizeof(NODE));
    int local_socket = -1;
    create_local_node(local_host);
    
    int actions_executed = 0;
    int next_action = 0;

    // REMAINING ACTIONS
    int remaining_actions = action_totals;
    
    while (actions_executed < remaining_actions)
    {   
        // printf("ACTION NUMBER: %i\n", next_action);
        // printf("ACTIONS EXECUTED: %i\n", actions_executed);
        // printf("ACTIONS LEFT: %i\n", remaining_actions);
        // printf("NUMBER OF HOSTS IN QUOTE QUEUE: %i\n", quote_queue);
        
        if(next_action < remaining_actions)
        {
            // LOCAL 
            if( !actions[next_action].is_remote )
            {
                int socket_desc = create_conn(local_host->ip, local_host->port);
                // printf("APPEND\n");
                printf("LOCAL %i\n",socket_desc);
                local_host->sock = socket_desc;
                local_socket = socket_desc;
                local_host->curr_req = CMD_SEND_FILE;
                local_host->actions = &actions[next_action];
                FD_SET(socket_desc, &output_sockets);
                ++next_action;
                ++curr_quote_req;
            }

            if( (curr_quote_req == next_action) && (actions[next_action].is_remote) && (quote_recv == 0) )
            {
                printf("REMOTE ACTION - BUILDING QUOTE FD_SET...\n");
                // BUILDING THE FD_SET
                NODE *temp = NULL;
                for (size_t i = 0; i < n_hosts; i++)
                {   
                    int sock = create_conn(hosts[i].name, hosts[i].port);
                    printf("%i\n", sock);
                    NODE *new_node = (NODE*)malloc(sizeof(NODE));
                    create_node(new_node, hosts[i].name, hosts[i].port);
                    FD_SET(sock, &output_sockets);
                    new_node->sock = sock;
                    new_node->curr_req = CMD_QUOTE_REQUEST;
                    if(temp == NULL) temp = new_node;
                    else append_new_node(temp, new_node); 
                }
                ++curr_quote_req;
            }
            // TODO: LOOP THROUGH ALL HOSTS TO SEND TO FIND QUOTE
            else if( (next_action < remaining_actions) && (quote_recv == n_hosts) )
            {   
                //printf("PICKING LOWEST COST...\n");
                char ip[MAX_LINE_LENGTH];
                int port = -1;
                get_lowest_cost(quote_list, ip, &port);
                int socket_desc = create_conn(ip, port);
                // printf("APPEND\n");
                NODE *slave = (NODE*)malloc(sizeof(NODE));
                create_node(slave, ip, port);
                slave->sock = socket_desc;
                slave->curr_req = CMD_SEND_FILE;
                slave->actions = &actions[next_action];
                append_new_node(conn_list, slave);
                FD_SET(socket_desc, &output_sockets);
                //printf("SUCCESS\n");
                next_action++;
            }

        }

        struct timeval tv;
        tv.tv_sec = 20;

        printf("SELECTING....\n");
        int activity = select(FD_SETSIZE+1, &input_sockets, &output_sockets, NULL, &tv);
        printf("SELECT RESULT: %i\n", activity);
        switch (activity)
        {
            case -1:
                perror("select()\n");
                close_all_sockets();
                break;
            case 0:
                perror("select() returned 0\n");
                break;
            default:

                for (size_t i = 0; i < FD_SETSIZE; i++)
                {   
                    printf("INPUT AT INDEX %li\n", i);
                    if (FD_ISSET(i, &input_sockets))
                    {   
                        //sleep(2);
                        int preamble = recv_byte_int(i);
                        //printf("PREAMBLE NUMBER: %d\n", preamble);

                        if(preamble == CMD_ACK)
                        {   
                            //printf("ACKNOWLEDGEMENT RECEIVED\n");
                            FD_CLR(i, &input_sockets);
                            FD_SET(i, &output_sockets);
                        }

                        if(preamble == CMD_QUOTE_REPLY)
                        {   
                            //recv_cost_reply(i);
                            int cost = recv_byte_int(i);
                            printf("COST RECEIVED: %i\n", cost);
                            add_cost(quote_list, i, cost);
                            ++quote_recv;
                            FD_CLR(i, &input_sockets);
                        }

                        if(preamble == CMD_RETURN_STATUS)
                        {
                            int return_code = recv_byte_int(i);
                            printf("RETURN CODE: %d\n", return_code);
                            if (return_code == 0)
                            {
                                preamble = recv_byte_int(i);
                                printf("RECEIVED: %i\n", preamble);
                                //change_state(i, preamble);
                            }
                        }
                        
                        // TODO: print error msg to screen
                        if (preamble == CMD_RETURN_STDOUT)
                        {
                            int return_code = recv_byte_int(i);
                            if (return_code > 0 && return_code < 5)
                            {   
                                int size = recv_byte_int(i);
                                char err_msg[size];
                                recv_string(i, err_msg, size);
                                printf("Errno: %i/n", return_code);
                                fputs(err_msg, stdout);
                                FD_CLR(i, &input_sockets);
                                if(i == local_socket)
                                {
                                    close_local_sock(local_host, &local_socket);
                                }
                                else
                                {
                                    remove_sd(conn_list, i);
                                }
                                
                            }
                        }
                        
                        else if (preamble == CMD_RETURN_STDERR)
                        {
                            int return_code = recv_byte_int(i);
                            if (return_code > 5)
                            {
                                int size = recv_byte_int(i);
                                char err_msg[size];
                                recv_string(i, err_msg, size);
                                printf("Errno: %i/n", return_code);
                                fputs(err_msg, stderr);
                                FD_CLR(i, &input_sockets);
                                if(i == local_socket)
                                {
                                    close_local_sock(local_host, &local_socket);
                                }
                                else
                                {
                                    remove_sd(conn_list, i);
                                }
                            }
                        }

                        else if(preamble == CMD_RETURN_FILE)
                        {
                            recv_bin_file(i);
                            FD_CLR(i, &input_sockets);
                            // printf("INCREMENTING ACTIONS EXECUTED\n");
                            ++actions_executed;
                            FD_CLR(i, &input_sockets);
                            if(i == local_socket)
                            {
                                close_local_sock(local_host, &local_socket);
                            }
                            else
                            {
                                remove_sd(conn_list, i);
                            }
                        }

                        else if(preamble == CMD_NO_OUTPUT)
                        {   
                            int return_code = recv_byte_int(i);
                            printf("NO OUTPUT FILE... RETURN CODE %i\n", return_code);
                            if(return_code == 0)
                            {
                                printf("RETURN CODE 0\n");
                            }
                            FD_CLR(i, &input_sockets);
                            ++actions_executed;
                            if(i == local_socket)
                            {
                                close_local_sock(local_host, &local_socket);
                            }
                            else
                            {
                                remove_sd(conn_list, i);
                            }
                        }
                    }

                    if (FD_ISSET(i, &output_sockets))
                    {   
                        printf("OUTPUT AT INDEX %li\n", i);
                        CMD curr_req = get_curr_req(local_host, conn_list, quote_list, i);
                        printf("CURRENT: %i\n", curr_req);
                        if(curr_req == CMD_QUOTE_REQUEST)
                        {   
                            // printf("SENDING COST REQUEST\n");
                            send_cost_req(i);
                            // REMOVE FROM OUTPUT
                            FD_CLR(i, &output_sockets);
                            // ADD TO INPUT
                            FD_SET(i, &input_sockets);
                            printf("WAITING...\n");
                        }
                        else if(curr_req == CMD_SEND_FILE)
                        {
                            NODE *curr = get_node(local_host, conn_list, i);
                            int file_count = curr->actions->req_count;
                            if (file_count > 1)
                            {   
                                char *next_file_to_send = curr->actions->requirements[file_count-1];
                                send_file(i, next_file_to_send);

                                // WAIT FOR ACK FROM SERVER BEFORE SENDING THE NEXT FILE
                                curr->actions->req_count--;
                                FD_CLR(i, &output_sockets);
                                FD_SET(i, &input_sockets);
                            }
                            else
                            {   
                                char *cmd = curr->actions->command;
                                send_cmd(i, cmd);
                                
                                // WAIT FOR RETURN STATUS
                                FD_CLR(i, &output_sockets);
                                FD_SET(i, &input_sockets);
                            }
                        }
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
    //init_nodes(hosts, num_hosts);
    //print_sock_list(sockets);
    //print_action_sets(action_set, num_sets);
    
    //printf("SETS %i\n", num_sets);

    for (size_t i = 0; i < num_sets; i++)
    {   
        handle_conn(hosts, num_hosts, action_set[i].actions, action_set[i].action_totals);
    }

    return 0; 
}
