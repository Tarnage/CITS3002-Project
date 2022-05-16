#include "parse_c.h"
//----------------------------------------------



char *trim_whitespace(char *str)
{
    char *end;

    // Trim leading space
    while(isspace((unsigned char)*str)) str++;

    if(*str == 0)  // All spaces?
    return str;

    // Trim trailing space
    end = str + strlen(str) - 1;
    while(end > str && isspace((unsigned char)*end)) end--;

    // Write new null terminator character
    end[1] = '\0';

    return str;
}


void file_process(char *file_name, ACTION_SET *action_set, HOST *hosts)
{
    FILE *fp = fopen(file_name, "r");
    if(fp == NULL)
    {
        fprintf(stderr, "Invalid file\n");
        exit(EXIT_FAILURE);
    }

    
    char line[MAX_LINE_LENGTH] = "";

    // READ AND PARSE FILES LINE BY LINE
    while(fgets(line, MAX_LINE_LENGTH, fp))
    {
        if (line[0] == '#')
        {
            continue;
        }
        // CHECK IF THE LINE GIVES THE DEFAULT PORT NUMBER
        if(strstr(line, "PORT") != NULL)
        {
            // Grab default port value
            int i = 0;
            while ( !isdigit(line[i]) )
            {
                i++;
            }
            char *port_val = &line[i];
            default_port = atoi(port_val);
            printf("DEFAULT PORT: %i\n", default_port);
        }

        // CHECK IF THE LINE GIVES THE HOST NAMES
        if(strstr(line, "HOSTS") != NULL)
        {   
            int nwords = 0;
            char **words = strsplit(line, &nwords);

            // START FROM 2 BECAUSE 0 AND 1 ARE NOT NEEDED
            for(int i = 2; i < nwords; i++)
            {   
                // IF STRING DOES NOT CONTAIN : MEANS IT HOST NEEDS DEFAULT POST
                if( strstr(words[i], ":") == NULL )
                {
                    hosts->name = trim_whitespace(words[i]);
                    hosts->port = default_port;
                    // printf("ADDED A HOST AND PORT, %s:%i\n", hosts->name, hosts->port);
                    hosts++;
                } 
                else 
                {   // WE GRAB THE PORT NUMBER FROM THE STRING
                    char *name = trim_whitespace(words[i]);
                    char *port = strstr(words[i], ":");
                    port[0] = '\0';
                    ++port;
                    hosts->name = strdup(name);
                    hosts->port = atoi(port);
                    // printf("ADDED A HOST AND PORT, %s:%i\n", hosts->name, hosts->port);
                    hosts++;
                }
                num_hosts++;
            }
        }

        if (strstr(line, "actionset") != NULL && line[0] != '\t') 
        {
            num_sets++;
        }
        
        // CHECK FOR TABS
        if (line[0] == '\t')
        {   
            int action_index = action_set[num_sets-1].action_totals;
            // IS NOT A DOUBLE 
            if(line[1] != '\t')
            {   
                // CHECKS IF THIS IS A REMOTE COMMAND
                if (strstr(line, "remote-") != NULL)
                {
                    ACTION_DATA(num_sets-1, action_index).is_remote = true;
                    int j = 0;
                    while (line[j] != '-')
                    {   
                        j++;
                    }
                    j++;
                    char *cmd = &line[j];
                    ACTION_DATA(num_sets-1, action_index).command = strdup(cmd);
                }
                else
                {
                    ACTION_DATA(num_sets-1, action_index).is_remote = false;
                    char *buffer = trim_whitespace(line);
                    ACTION_DATA(num_sets-1, action_index).command = strdup(buffer);
                }
                action_set[num_sets-1].action_totals++;
            }
            // ELSE IS A DOUBLE
            else
            {   
                // GO BACK AN INDEX TO FILL OUT REQUIREMENTS 
                --action_index;
                char *buffer = trim_whitespace(line);
                ACTION_DATA(num_sets-1, action_index).requirements = strsplit(buffer, &ACTION_DATA(num_sets-1, action_index).req_count);
            }
        }
    }
}

void print_hosts(HOST *hosts, int size)
{   

    // CAN ALSO ITERATE USING GLOBAL VAR num_hosts
    while (hosts != NULL)
    {
        if(hosts->name == NULL){
            break;
        }
        printf("IP ADDR = (%s,%i)\n", hosts->name, hosts->port);
        ++hosts;
    }
    
}


void print_action_sets(ACTION_SET *sets, int size)
{
    for (size_t i = 0; i < size; i++)
    {   
        size_t action_count = sets[i].action_totals;
        for (size_t j = 0; j < action_count; j++)
        {
            char *cmd       = sets[i].actions[j].command;
            int remote      = sets[i].actions[j].is_remote;
            int req_count   = sets[i].actions[j].req_count;
            char **reqs     = sets[i].actions[j].requirements;
            
            printf("CMD: %s\n", cmd);
            printf("Is it a remote command: %i\n", remote);

            if (req_count > 0)
            {
                printf("Required Files\n");
                for (size_t k = 1; k < req_count; k++)
                {
                    printf("%s ", reqs[k]);
                }
                printf("\n");
            }

        }
        
    }
    
}

void print_array_words(char **words, int len)
{
    for(int i = 0; i < len; i++){
        printf("%s ", words[i]);
    }
}
