#include "rake-c.h"

#ifndef __APPLE__
// NOT STANDARD LIB CAN INSTALL WITH sudo apt -y install libexplain-dev
#include <libexplain/connect.h>
#endif

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
#define LOCAL_HOST   "127.0.0.1"
#define MAX_BYTES    1024
#define MAX_SOCKETS  FD_SETSIZE
//#define USE_FIND_FILE

//--------------------GLOBALS-------------------
int num_sockets = 0;
NODE *sockets;


// FILLS STRUCTS WITH RAKEFILE CONTENTS
void init_actions(char *file_name, ACTION_SET *actions, HOST *hosts)
{
    file_process(file_name, actions, hosts);
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


void send_byte_int(int sd, CMD preamble)
{
    // CONVERT TO HOST TO NETWORK BYTE ORDER (BIG EDIAN)
    // ALWAYS CONVERTS INTS TO 4 BYTES LONG
    int cmd  = htonl( preamble );

    // SEND THE REQ
    printf("SENDING INT ----> %d\n", preamble);
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
    printf("BYTE COUNT SHOULD BE 4 == %i\n", byte_count);
    if(byte_count == 0){
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
    printf("SENDING FILE ----> %s\n", payload);
    // free(result);
}


// SEND TEXT FILE TO SERVER
void send_file(int sd, char *filename)
{
    send_byte_int(sd, CMD_SEND_FILE);
    printf("SENDING FILE ----> %s\n", filename);
    
#ifdef USE_FIND_FILE
    char *path = find_file(filename);
#else
    char *path = filename;
#endif

    send_string(sd, filename);

    FILE *fp = fopen(path, "rb");

    if (fp == NULL)
    {
        exit(EXIT_FAILURE);
    }
    else 
    {
        struct stat st;
        stat(path, &st);
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

    printf("STRING RECEIVED: %s\n", string);
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
    // printf("SIZE OF FILE NAME: %d\n", str_size);
    char filename[str_size]; 

    // RECEIVE THE FILENAME 
    recv_string(sock, filename, str_size);
    // printf("%s\n", filename);

    // RECEIVE THE SIZE OF THE FILE
    // printf("RECEIVING FILE SIZE\n");
    int file_size = recv_byte_int(sock);
    // printf("FILE SIZE: %d BYTES\n", file_size);

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
    // printf("%s\n", dir_for_file);

    
    // OPEN THE FILE
    FILE *fp = fopen(dir_for_file, "wb");
    if (fp == NULL)
    {
        printf("PROBLEM\n");
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
void init_nodes(HOST *hosts)
{    
    sockets = (NODE*)malloc(sizeof(NODE));

    // FIRST NODE ALWASY LOCAL HOST
    sockets->ip = LOCAL_HOST;
    sockets->port = default_port;
    sockets->used = true;       // LOCAL HOST IS RESERVED FOR LOCAL EXECUTION 
    sockets->cost = INT_MAX;
    sockets->curr_req = -1;
    sockets->local = true;
    sockets->next = (NODE*)malloc(sizeof(NODE));

    NODE *head = sockets->next;
    while(hosts->name != NULL)
    {   
        if (head == NULL)
        {
            head = (NODE*)malloc(sizeof(NODE));
        }
        head->ip = hosts->name;
        head->port = hosts->port;
        head->used = false;
        head->cost = INT_MAX;
        head->curr_req = -1;
        sockets->local = false;
        head->next = NULL;

        head = head->next;
        ++hosts;
    }
}


// FOR TESTING PRINT THE CURRENT SOCK LIST
void print_sock_list(NODE *list)
{   
    int i = 0;
    printf("CURRENT SOCKET LIST\n");
    while(i != num_sockets)
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


void reset_socket_node(NODE *list)
{   
    list->sock = -1;
    list->cost = INT_MAX;
    list->used = false;
    list->curr_req = -1;
}


NODE* get_lowest_cost()
{
    NODE *low_host = (NODE*)malloc(sizeof(NODE));
    // COPYING THE HEAD OF THE GLOBAL VAR
    // DONT CHECK THE FIRST ONE AS ITS THE LOCAL HOST
    // AND LOCAL HOST NEVER NEEDS TO SEND REQ COSTS
    NODE *list = sockets->next;
    int min = list->cost;
    low_host = list;

    reset_socket_node(list);

    list = list->next;

    while(list != NULL)
    {
        if(list->cost < min)
        {
            low_host = list;
            min = list->cost;
        }

        reset_socket_node(list);
        list = list->next;
    }

    return low_host; 
}

void make_free(NODE *sockets, int sd)
{
    while(sockets->sock != sd) ++sockets;
    sockets->used = false;
}

// HELPER TO FIND WHAT REQ THE SOCKET IS DOING
// i.e. ARE THEY JUST ASKING FOR A COST REQUEST OR ARE THEY SENDING A FILE
CMD get_curr_req( int sd) 
{   
    CMD result = -1;

    NODE *head = sockets;
    while(head != NULL)
    {
        if(head->sock == sd)
        {
            result = head->curr_req;
            return result;
        }
        head = head->next;
    }

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
    printf("COST RECEIVED: %d\n", cost);
    add_quote(sd, cost);
}


void send_cost_req(int sd)
{   
    printf("SENDING COST REQUEST ---->\n");
    send_byte_int(sd, CMD_QUOTE_REQUEST);
    // SET THE NODE TO EXPECT A REPLY
    change_state(sd, CMD_QUOTE_REPLY);
}


NODE *get_node(int sd)
{
    NODE *head = sockets;
    while(head->sock != sd) head = head->next;
    return head;
}


void send_cmd(int sd, char *cmd)
{   
    printf("SENDING COMMAND ----> %s\n", cmd);
    // TODO send command to server to execute
    send_byte_int(sd, CMD_EXECUTE);
    send_string(sd, cmd);
}



// MAIN CONNECTION HANDLER
void handle_conn(NODE *sockets, ACTION* actions, HOST *hosts, int action_totals) 
{
    // SOCKETS TO READ FROM
    fd_set input_sockets;
    FD_ZERO(&input_sockets);

    // SOCKETS TO WRITE TO
    fd_set output_sockets;
    FD_ZERO(&output_sockets);

    // INDEX TO SET
    int actions_executed = 0;

    // IF CURRENT ACTION IS LAST ONE, DON'T SEND OUT COST REQUESTS
    int current_action = 0;

    // REMAINING ACTIONS
    int actions_left = action_totals;

    // SOCKETS REQUESTING COST
    int quote_queue = 0;

    // WAITING FOR CALCULATION?
    bool cost_waiting = false;

    // int sigma; 
    
    while (actions_executed < actions_left)
    {   
        printf("CURR %i\n", current_action);
        printf("executed %i\n", actions_executed);
        printf("actions left %i\n", actions_left);
        printf("quote queue %i\n", quote_queue);
        if(quote_queue == 0 && cost_waiting)
        {
            // CHECK WHEN THERE ARE COSTS FOR NEXT COMMAND CALCULATION
            // THEN USE THE LOWEST RETURN CONNECTION TO EXECUTE THE NEXT ACTION
            if( actions[current_action].is_remote )
            {   
                printf("PICKING LOWEST COST...\n");
                NODE *slave = get_lowest_cost();
                cost_waiting = false;

                int socket_desc = create_conn(slave->ip, slave->port);
                // printf("APPEND\n");
                slave->sock = socket_desc;
                slave->used = true;
                slave->curr_req = CMD_SEND_FILE;
                slave->actions = &actions[current_action];
                FD_SET(socket_desc, &output_sockets);
                current_action++;
            }
        }

        // ACTIONS LEFT FOR EXECUTION
        if(current_action < actions_left)
        {
            // LOCAL 
            if( !actions[current_action].is_remote )
            {
                // RUN PROCESS - USE system()??
                // FIRST NODE IN sockets IS THE LOCAL_HOST
                int socket_desc = create_conn(sockets->ip, sockets->port);
                // printf("APPEND\n");
                sockets->sock = socket_desc;
                sockets->curr_req = CMD_SEND_FILE;
                sockets->actions = &actions[current_action];
                FD_SET(socket_desc, &output_sockets);
                ++current_action;
            }

            if (current_action < actions_left)
            {   
                printf("BUILDING FD_SET...\n");
                // BUILDING THE FD_SET
                // HEAD IS LOCAL HOST
                NODE *head = sockets->next;
                while(head != NULL)
                {   
                    if( (!head->used) && (!head->local) )
                    {   
                        printf("BUILDING\n");
                        int socket_desc = create_conn(head->ip, head->port);
                        head->sock = socket_desc;
                        head->used = true;
                        head->curr_req = CMD_QUOTE_REQUEST;
                        quote_queue++;
                        FD_SET(socket_desc, &output_sockets);
                    }
                    head = head->next;
                }
                
            }
        }

        struct timeval tv;
        tv.tv_sec = 5;

        printf("SELECTING....\n");
        int activity = select(FD_SETSIZE+1, &input_sockets, &output_sockets, NULL, &tv);
        printf("ACTIVITY %i\n", activity);
        switch (activity)
        {
        case -1:
            perror("select()\n");
            close_all_sockets();
            break;
        case 0:
            perror("select() returned 0\n");
            close_all_sockets();
            break;
        default:

            for (size_t i = 0; i < FD_SETSIZE; i++)
            {
                if (FD_ISSET(i, &input_sockets))
                {   
                    //sleep(2);
                    int preamble = recv_byte_int(i);
                    printf("PREAMBLE NUMBER: %d\n", preamble);

                    if(preamble == CMD_ACK)
                    {   
                        printf("ACKNOWLEDGEMENT RECEIVED\n");
                        FD_CLR(i, &input_sockets);
                        FD_SET(i, &output_sockets);
                    }

                    else if(preamble == CMD_QUOTE_REPLY)
                    {   
                        //recv_cost_reply(i);
                        int cost = recv_byte_int(i);
                        printf("COST RECEIVED: %i\n", cost);
                        quote_queue--;
                        cost_waiting = true;
                        FD_CLR(i, &input_sockets);
                    }

                    else if(preamble == CMD_RETURN_STATUS)
                    {
                        int return_code = recv_byte_int(i);
                        // printf("RETURN CODE: %d\n", return_code);
                        if (return_code == 0)
                        {
                            // change_state(i, CMD_RETURN_FILE);
                            preamble = recv_byte_int(i);
                        }
                    }
                    
                    else if (preamble == CMD_RETURN_STDOUT)
                    {
                        continue;
                    }
                    
                    else if (preamble == CMD_RETURN_STDERR)
                    {
                        continue; 
                    }

                    else if(preamble == CMD_RETURN_FILE)
                    {
                        recv_bin_file(i);
                        FD_CLR(i, &input_sockets);
                        ++actions_executed;

                        // MARK UNUSED
                        NODE *node = get_node(i);
                        node->used = false;
                        close(i);
                    }

                    else if(preamble == CMD_NO_OUTPUT)
                    {   
                        int return_code = recv_byte_int(i);
                        FD_CLR(i, &input_sockets);
                        printf("NO OUTPUT FILE... RETURN CODE %i\n", return_code);
                        ++actions_executed;
                        //close(i);
                    }
                }

                if (FD_ISSET(i, &output_sockets))
                {   
                    sleep(2);
                    CMD curr_req = get_curr_req(i);
                    if(curr_req == CMD_QUOTE_REQUEST)
                    {   
                        printf("SENDING COST REQUEST\n");
                        send_cost_req(i);
                        // REMOVE FROM OUTPUT
                        FD_CLR(i, &output_sockets);
                        // ADD TO INPUT
                        FD_SET(i, &input_sockets);
                        printf("WAITING...\n");
                    }
                    else if(curr_req == CMD_SEND_FILE)
                    {
                        NODE *curr = get_node(i);
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
    ACTION_SET action_set[MAX_ACTIONS];


    init_actions(file_name, action_set, hosts);
    init_nodes(hosts);

#define COMMAND(i,j)     action_set[i].actions[j]
    
    for (size_t i = 0; i < num_sets; i++)
    {   
        handle_conn(sockets, action_set[i].actions, hosts, action_set[i].action_totals);
    }

    return 0; 
}
