#ifndef STRUCTURES_H
#define STRUCTURES_H

//-----------------------------------STRUCTURES------------------------------------------

// COMMANDS
typedef enum _cmd{
    CMD_DEBUG = 0,

    CMD_QUOTE_REQUEST,
    CMD_QUOTE_REPLY,

    CMD_BIN_FILE,
    CMD_SEND_FILE,

    CMD_EXECUTE,
    CMD_RETURN_STATUS,
    CMD_RETURN_STDOUT,
    CMD_RETURN_STDERR,
    CMD_RETURN_FILE,
    
    CMD_ACK,
    CMD_NO_OUTPUT
} CMD;

// STORE ACTIONS
typedef struct _action
{
    char *command; 
    bool is_remote;
    int req_count;
    char **requirements; 
} ACTION;

// STORE HOST DETAILS
typedef struct _host
{
    char *name;
    int port;
} HOST;

// STORE A SET OF ACTIONS
typedef struct _actionset
{
    ACTION actions[MAX_ACTIONS];
    int action_totals;
} ACTION_SET;


// A LINKED LIST 
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

#endif