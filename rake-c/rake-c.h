#ifndef RAKE_C_H
#define RAKE_C_H

#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <netdb.h>
#include <arpa/inet.h>
#include "parse_c.h"
#include <stdbool.h>
#include <sys/stat.h>
#include <limits.h>
#include <sys/select.h>
#include <fcntl.h>

#define MAX_BYTES_SIGMA 4
#define TEMP_FOLDER "./tmp/"
#define MAX_QUEUE_ITEMS 64

typedef enum _cmd{
    CMD_ECHO,
    CMD_ECHOREPLY,
    CMD_QUOTE_REQUEST,
    CMD_QUOTE_REPLY,
    CMD_SEND_REQUIREMENTS,
    CMD_BIN_FILE,
    CMD_SEND_FILE,
    CMD_SEND_SIZE,
    CMD_SEND_NAME,
    CMD_EXECUTE_REQ,
    CMD_EXECUTE,
    CMD_RETURN_STATUS,
    CMD_RETURN_STDOUT,
    CMD_RETURN_STDERR,
    CMD_RETURN_FILE,
    CMD_ACK,
    CMD_NO_OUTPUT
} CMD;


//---------------------STRUCTS----------------------------------


typedef struct _node
{
    int sock;
    char *ip;
    int port;
    int cost;
    CMD curr_req;
    ACTION *actions;
    struct _node *next;
    struct _node *prev;
    
} NODE;

// INIT FUNCTION FOR NODES
void create_node(NODE *new_node, char *ip, int port)
{
    new_node->sock = -1;
    new_node->ip = ip;
    new_node->port = port;
    new_node->next = NULL;
    new_node->prev = NULL;
}

// APPEND NEWLY CREATED NODE TO HEAD
void append_new_node(NODE *head, NODE *new_node)
{
    NODE *temp = head;
    while(temp->next != NULL) temp = temp->next;
    temp->next = new_node;
    new_node->prev = temp;
}


void free_list(NODE *pList)
{
    NODE* temp;
    while(pList != NULL)
    {
        temp = pList;
        pList = pList->next;
        free(temp);
    }
}

// REMOVE NODE ASSOCIATED TO THE SOCK FD
// ALSO CLOSES THE SOCK FD
void remove_sd(NODE *conn_list, int sd)
{
    NODE *temp = conn_list;
    
    while(temp->sock != sd) temp = temp->next;
    shutdown(temp->sock, SHUT_RDWR);
    close(temp->sock);
    
    // ITS THE HEAD
    if (temp->prev == NULL)
    {   
        //ITS THE ONLY ONE IN THE LIST
        if (temp->next == NULL) 
        {
            conn_list = NULL;
        }
        else
        {
            NODE *new_head = temp->next;
            temp->prev = NULL;
            conn_list = new_head;
        }
    }
    // ITS THE TAIL
    else if (temp->next == NULL)
    {
        temp->prev->next = NULL;
    }
    // ITS IN THE MIDDLE
    else
    {
        NODE *prev = temp->prev;
        temp->next->prev = prev;
        prev->next = temp->next;
        
    }
    free(temp);
}

void add_cost(NODE *head, int sd, int cost)
{
    NODE *temp = head;
    while(temp->sock != sd) 
    {
        temp = temp->next;
    }
    
    temp->cost = cost;
    shutdown(temp->sock, SHUT_RDWR);
    close(temp->sock);
    temp->sock = -1;
}


void close_local_sock(NODE *local, int *sd)
{   
    shutdown(local->sock, SHUT_RDWR);
    close(local->sock);
    local->sock = -1;
    *sd = -1;
}


#endif
