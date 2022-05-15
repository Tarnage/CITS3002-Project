#include "rake-c.h"

#ifndef __APPLE__
// NOT STANDARD LIB CAN INSTALL WITH sudo apt -y install libexplain-dev
#include <libexplain/connect.h>
#endif

#define SERVER_PORT  6327
#define SERVER_HOST  "127.0.0.1"
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

void send_byte_int(int sd, CMD ack_type)
{
     // CONVERT TO HOST TO NETWORK BYTE ORDER (BIG EDIAN)
    // ALWAYS CONVERTS INTS TO 4 BYTES LONG
    int cmd  = htonl( ack_type );

    // SEND THE REQ
    printf("SENDING BYTE: %d\n", ack_type);
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

    if(byte_count == 0){
        printf("INTEGER NOT RECEIVED\n");
        exit(EXIT_FAILURE);
    }
	uint32_t result = 0;
    memcpy(&result, buffer, MAX_BYTES_SIGMA);

    return ntohl(result);
}


// HELPER TO ADD COST TO SOCK LIST 
void add_quote(int sock, int quote)
{
    NODE *tmp = sockets;
    printf("APPENDING CURRENT QUOTE: %i\n", quote);
    while(tmp->sock != sock) ++tmp;
    tmp->cost = quote;
}


// SEND REQ AND RECEIVE QUOTES
void send_quote_req(int sock)
{   
    send_byte_int(sock, CMD_QUOTE_REQUEST);

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


void send_string(int sd, char *payload)
{
	
	int size = strlen(payload);
    printf("SENDING SIZE: %d\n", size);
	send_byte_int(sd, size);
    
	send(sd, payload, size, 0);
    printf("SENT SUCCESSFULLY\n");
    // free(result);
}


// SEND TEXT FILE TO SERVER
void send_txt_file(int sd, char *filename)
{
    send_byte_int(sd, CMD_SEND_FILE);
    
#ifdef USE_FIND_FILE
    char *path = find_file(filename);
#else
    char *path = filename;
#endif

    send_string(sd, filename);

    FILE *fp = fopen(path, "r");

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
        // printf("%s\n", buffer);
        send_byte_int(sd, size);
        send(sd, buffer, size, 0);
        // exit(EXIT_SUCCESS);
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

    // printf("%s\n", string);
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
    printf("SIZE: %d\n", str_size);
    char filename[str_size]; 

    // RECEIVE THE FILENAME 
    recv_string(sock, filename, str_size);
    printf("%s\n", filename);

    // RECEIVE THE SIZE OF THE FILE
    printf("RECEIVING FILE SIZE\n");
    int file_size = recv_byte_int(sock);
    printf("FILE SIZE: %d BYTES\n", file_size);

    // TODO: MAKE THIS A CHECK FUNCTION
    // #DEFINE "./tmp/"
    // CAN REUSE THIS CHECK BEFORE EXECUTING LOCAL COMMANDS
    // SINCE WE MIGHT WANT TO RUN THE COMMANDS IN THIS DIR
    if(check_folder_exists(TEMP_FOLDER) != -1)
    {   
        // THERE A MACRO FOR 0777?
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

    printf("FILE RECEIVED SUCCESSFULLY\n");
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

void append_sockets(NODE* socket_appended, char *host, int port, int sd, bool used)
{
    // CHECK IF NODE IS EMPTY
    if(socket_appended == NULL)
    {
        socket_appended = (NODE*) malloc(sizeof(NODE));
        socket_appended->ip = host;
        socket_appended->port = port;
        socket_appended->sock = sd;
        socket_appended->used = used; 
    }
    else
    {
        // GO TO THE END 
        NODE* head = socket_appended;
        while(socket_appended != NULL)
        {
            ++socket_appended;
        }

        socket_appended = (NODE*)malloc(sizeof(NODE));
        socket_appended->ip = host;
        socket_appended->port = port;
        socket_appended->sock = sd;
        socket_appended->used = used;
        socket_appended->next = NULL;

        socket_appended = head; 
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
void init_nodes(NODE *list, HOST *hosts)
{   
    while(true)
    {   
        if (hosts->name == NULL)
        {
            break;
        }
        
        list->next = (NODE*)malloc(sizeof(NODE));

        list->ip = hosts->name;
        list->port = hosts->port;
        list->used = false;
        list->cost = INT_MAX;
        list->curr_req = -1;

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


// HELPER TO LOOP OVER ALL SOCKETS IN THE LIST AND GET THE COST
/*
void get_all_costs(NODE *list)
{
    int i = 0;
    printf("GETTING COST FOR ALL CONNECTIONS\n");
    while(i != num_sockets)
    {
        handle_conn(list->sock, NULL, CMD_QUOTE_REQUEST);
        ++list;
        ++i;
    }
} */

bool find(int queue[], int socket)
{
    bool found = false; 

    for (int i = 0; i < MAX_QUEUE_ITEMS; i++)
    {
        if(queue[i] == socket)
        {
            found = true;
        }
    }

    return found;
}

bool check_socket_exists (NODE *list, int sd)
{
    bool exists = false;

    NODE *head = list; 
    while(list->next != NULL)
    {
        if(list->sock == sd)
        {
            exists = true;
            break;
        }

        ++list;
    }
    list = head;

    return exists; 
}

NODE* get_lowest_cost ()
{
    NODE *low_host;
    // COPYING THE HEAD OF THE GLOBAL VAR
    NODE * list = sockets;
    int min = list->cost;
    low_host = list;
    list->used = false;
    list->cost = INT_MAX;
    list->curr_req = -1;
    list++;

    while(list->next != NULL)
    {
        if(list->cost < min)
        {
            low_host = list;
            min = list->cost;
        }
        list++;
        list->used = false;
        list->cost = INT_MAX;
        list->curr_req = -1;
    }

    return low_host; 
}

void make_free(NODE *sockets, int sd)
{
    while(sockets->sock != sd)
    {
        ++sockets;
    }

    sockets->used = false;
}

// HELPER TO FIND WHAT REQ THE SOCKET IS DOING
// i.e. ARE THEY JUST ASKING FOR A COST REQUEST OR ARE THEY SENDING A FILE
CMD get_curr_req(NODE *list, int sd) 
{   
    CMD result = -1;

    NODE *head = list; 
        while(list->next != NULL)
        {
            if(list->sock == sd)
            {
                result = list->curr_req;
                return result;
            }

            ++list;
        }
        list = head;

    return result;
}

// MAIN CONNECTION HANDLER
void handle_conn(/*int sock */NODE *sockets, ACTION* actions, HOST *hosts, int action_totals) 
{
    // SOCKETS TO READ FROM
    fd_set input_sockets;
    FD_ZERO(&input_sockets);

    // SOCKETS TO WRITE TO
    fd_set output_sockets;
    FD_ZERO(&output_sockets);

    // WHILE THERE IS A SOCKING WAITING TO SEND OR RECV, QUEUE >=1
    // MESSAGE QUEUE
    int messages[MAX_QUEUE_ITEMS];

    // ACK QUEUE
    int ack_queue[MAX_QUEUE_ITEMS];

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

    int sigma; 

    while (actions_executed < actions_left)
    {
        if(quote_queue == 0 && cost_waiting)
        {
            // CHECK WHEN THERE ARE COSTS FOR NEXT COMMAND CALCULATION
            // THEN USE THE LOWEST RETURN CONNECTION TO EXECUTE THE NEXT ACTION
            if(actions[current_action].is_remote == 1)
            {
                NODE *slave = get_lowest_cost();
                cost_waiting = false;

                int socket_desc = create_conn(slave->ip, slave->port);
                // printf("APPEND\n");
                slave->sock = socket_desc;
                slave->used = true;
                slave->curr_req = CMD_SEND_FILE;
                // printf("SETTING TO OUTPUT SOCKETS\n");
                FD_SET(socket_desc, &output_sockets);
            }
        }

        // ACTIONS LEFT FOR EXECUTION
        if(current_action < actions_left)
        {
            // LOCAL 
            if(actions[current_action].is_remote == 0)
            {
                // RUN PROCESS - USE system()??
                ++current_action;
                ++actions_executed; 
            }
            else
            {   
                // BUILDING THE FD_SET
                NODE *head = sockets; 
                while(sockets->next != NULL)
                {
                    if( !sockets->used )
                    {
                        printf("CREATING CONNECTION WITH HOST %s at PORT %d\n", sockets->ip, sockets->port);
                        int socket_desc = create_conn(sockets->ip, sockets->port);
                        // printf("APPEND\n");
                        sockets->sock = socket_desc;
                        sockets->used = true;
                        sockets->curr_req = CMD_QUOTE_REQUEST;
                        // printf("SETTING TO OUTPUT SOCKETS\n");
                        FD_SET(socket_desc, &output_sockets);
                    }
                    ++sockets;
                }
                sockets = head;
            }
        }




    //     // GET LIST OF READABLE SOCKETS
    //     if(select(FD_SETSIZE, &input_sockets, &output_sockets, NULL, 0) < 0)
    //     {
    //         perror("ERROR: ");
    //         exit(EXIT_FAILURE);
    //     }

    //     printf("ITERATING\n");
    //     for(int i = 0; i < FD_SETSIZE; i++)
    //     {
    //         // printf("CHECKING FOR SOCKET %d\n", i);
    //         if(check_socket_exists(sockets, i))
    //         {

    //             printf("WAITING FOR REPLY\n");
    //             if(FD_ISSET(i, &input_sockets))
    //             {
    //                 FD_CLR(i, &input_sockets);
    //             }
                
    //             // READ SOMETHING
    //             sigma = recv_byte_int(i);

    //             if(sigma == CMD_ACK)
    //             {
    //                 printf("SETTING SOCKET FOR WRITING\n");
    //                 FD_SET(i, &output_sockets);
    //             }
    //             else if(sigma == CMD_QUOTE_REPLY)
    //             {
    //                 int cost = recv_byte_int(i);
    //                 printf("RECEIVED COST: %d\n", cost);
    //                 add_quote(i, cost);
    //                 cost_waiting = true;
    //                 --quote_queue;
    //                 printf("CLOSING CONNECTION\n");
    //                 close(i);
    //             }
    //             else if (sigma == CMD_RETURN_STATUS)
    //             {
    //                 int r_code = recv_byte_int(i);
    //                 printf("RETURN CODE: %d\n", r_code);

    //                 if(r_code == 0)
    //                 {
    //                     // EXPECT FILE FROM SERVER
    //                     printf("REMOTE HOST EXECUTION SUCCESSFUL\n");
    //                     messages[i] = CMD_RETURN_FILE;
    //                 }
    //                 else if (r_code > 0 && r_code < 5)
    //                 {
    //                     printf("WARNING ERROR RECEIVED\n");
    //                     messages[i] = CMD_RETURN_STDOUT; 
    //                 }
    //                 else
    //                 {
    //                     printf("FATAL ERROR\n");
    //                     messages[i] = CMD_RETURN_STDERR;
    //                 }

    //                 FD_SET(i, &input_sockets);
    //             }
    //             else if(sigma == CMD_RETURN_FILE)
    //             {
    //                 printf("RECEIVING FILE\n");
    //                 recv_bin_file(i);
    //                 printf("CLOSING CONNECTION\n");
    //                 ++actions_executed;
    //                 make_free(sockets, i);
    //                 close(i);
    //                 messages[i] = 0;
    //             }
                
    //         }
    //     }

    //     for(int i = 0; i < FD_SETSIZE; i++)
    //     {
    //         if(check_socket_exists(sockets, i))
    //         {
    //             if(FD_ISSET(i, &output_sockets))
    //             {
    //                 FD_CLR(i, &output_sockets);
    //             }

    //             int msg_type = messages[i];
    //             printf("SENDING MESSAGE\n");

    //             // CHECK IF i is in ack_queue
    //             if(find(ack_queue, i))
    //             {
    //                 send_byte_int(i, CMD_QUOTE_REQUEST);
    //                 FD_SET(i, &input_sockets);
    //                 ack_queue[i] = 0; 
    //             }
    //             else if(msg_type == CMD_QUOTE_REQUEST)
    //             {
    //                 send_byte_int(i, CMD_QUOTE_REQUEST);
    //                 messages[i] = CMD_QUOTE_REQUEST;
    //                 FD_SET(i, &input_sockets);
    //             }
    //             else if(msg_type == CMD_SEND_FILE)
    //             {
    //                 if(actions->req_count == 0)
    //                 {
    //                     // DO SOMETHING
    //                     messages[i] = CMD_RETURN_STATUS;
    //                     FD_SET(i, &input_sockets);
    //                 }
    //                 else
    //                 {
    //                     actions->req_count--; 
    //                     // TODO ADD find_file() CHECK HERE.
    //                     printf("SENDING FILE: %s\n", actions->requirements[actions->req_count]);
    //                     send_txt_file(i, actions->requirements[actions->req_count]);
    //                     actions->req_count--;
    //                     int ack = recv_byte_int(i);
    //                     if(ack != CMD_ACK)
    //                     {
    //                         printf("SOMETHING WENT WRONG\n");
    //                     }

    //                     messages[i] = CMD_SEND_FILE;
    //                     FD_SET(i, &input_sockets);
    //                 }
    //             }
    //         }
            
    //     }

    //     actions_executed++;
    //     current_action++;
    
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
    sockets = (NODE*)malloc(sizeof(NODE));


    init_actions(file_name, action_set, hosts);
    init_nodes(sockets, hosts);
    //print_hosts(hosts, host_count);
    //print_action_sets(action_set, action_count);

#define COMMAND(i,j)     action_set[i].actions[j]
    for (size_t i = 0; i < num_sets; i++)
    {   
        handle_conn(sockets, action_set->actions, hosts, action_set[i].action_totals);
        /*
        size_t action_count = action_set[i].action_totals;
        for (size_t j = 0; j < action_count; j++)
        {   
            // CHECK IF ITS A REMOTE COMMAND
            if(COMMAND(i,j).is_remote != 1)
            {   
                //TODO: HANDLE LOCAL EXECUTIONS
                
                if(COMMAND(i,j).req_count > 0)
                {
                    for (size_t k = 1; k < COMMAND(i, j).req_count; k++)
                    {
                        if(fopen(COMMAND(i,j).requirements[k], "r") == NULL)
                        {
                            break; 
                        }
                    }
                    system(COMMAND(i,j).command);
                } 
            }
            else
            {   
                fd_set sockets_created; //sockets_used; 

                // INITIALIZE THE SET OF CONNECTIONS
                FD_ZERO(&sockets_created);

                // TODO: GET THE LOWEST COST
                get_all_conn(sockets, hosts, sockets_created);

                
                while(true)
                {
                    sockets_used = sockets_created; 
                    if(select(FD_SETSIZE, &sockets_used, NULL, NULL, NULL) < 0)
                    {
                        perror("ERROR USING SELECT");
                        exit(EXIT_FAILURE);
                    }

                    for(int i = 0; i < FD_SETSIZE; i++)
                    {
                        if(FD_ISSET(i, &sockets_used))
                        {
                            
                        }
                    }

                    
                } 

                get_all_costs(sockets);
                    
                print_sock_list(sockets);

                HOST *slave = get_lowest_cost(sockets);
                printf("LOWEST HOST: %s:%i\n", slave->name, slave->port);
                    
                int slave_sock = create_conn(slave->name, slave->port);

                if(COMMAND(i,j).req_count > 0)
                {
                    // TODO: HANDLE FILE TRANSFERS
                    handle_conn(slave_sock, &COMMAND(i,j), CMD_SEND_FILE);
                }
                else
                {
                    // TODO: NO FILE REQS JUST RUN SEND THE COMMAND
                    handle_conn(slave_sock, &COMMAND(i,j), CMD_EXECUTE);
                }
            }

        }*/
        
    }

    // perform_actions(action_set);

    return 0; 
}
