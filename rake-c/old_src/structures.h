#ifndef STRUCTURES_H
#define STRUCTURES_H
// CONSTANTS
#define MAX_ACTIONS     32
#define MAX_SETS        16
#define MAX_HOSTS       32

// STRUCTURES
typedef struct _action
{
    char *command; 
    int is_remote;
    int req_count;
    char **requirements; 
} ACTION;

typedef struct _host
{
    char *name;
    int port;
} HOST;

typedef struct _actionset
{
    ACTION actions[MAX_ACTIONS];
    int action_totals;
} ACTION_SET;

#endif 