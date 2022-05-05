#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <ctype.h>
#include "strsplit.c"

#define MAX_LINE_LENGTH 80

// HOST STRUCT
typedef struct host
{
    char *name;
    int port;
} HOST;

// STRUCT FOR ACTION
typedef struct action
{
    int is_remote;
    char *command; 
    int num_req;
    char **requirements; 

} ACTION;

// STRUCT FOR ACTION SETS
typedef struct action_set
{
    int num_actions;
    ACTION *actions; 
} ACTION_SET;

int num_sets;
void remove_str(char *line, char stop_char, char *intended)
{
    int counter_line = 0;
    int new_word_counter = 0;


    while(line[counter_line] != stop_char)
    {
        counter_line++;
    }
    
    counter_line++;

    while(line[counter_line] != '\0')
    {
        intended[new_word_counter] = line[counter_line];
        
        new_word_counter++;
        counter_line++;
    }

    intended[new_word_counter] = '\0';
}

void file_process(char *file_name, ACTION_SET *sets, HOST *hosts)
{
    FILE *fp = fopen(file_name, "r");
    if(fp == NULL)
    {
        fprintf(stderr, "Invalid file\n");
    }
    else
    {
        int curr_set = 0;
        int curr_action = 0;

        int curr_req = 0;
        

        sets[curr_set].num_actions = 0;
        sets[curr_set].actions = (ACTION*)malloc(sizeof(ACTION));
        sets[curr_set].actions[curr_action].requirements = (char**)malloc(sizeof(char*));
        sets[curr_set].actions[curr_action].num_req = 0;

        char line[MAX_LINE_LENGTH] = "";
        
        int default_port = 0;
        int curr_host = 0;
        int cust_port = 0;
        // int num_hosts = 0;

        // READ AND PARSE FILES LINE BY LINE
        while(fgets(line, MAX_LINE_LENGTH, fp))
        {
            if (line[0] == '#')
            {
                continue;
            }

            if(strstr(line, "PORT") != NULL)
            {
                // Grab default port value
                char port_val[MAX_LINE_LENGTH] = "";
                remove_str(line, '=', port_val);

                default_port = atoi(port_val);
                
            }

            if(strstr(line, "HOSTS") != NULL)
            {
                int nhosts;
                char host_names[MAX_LINE_LENGTH] = "";
                remove_str(line, '=', host_names);
                char **host_name_list = strsplit(host_names, &nhosts);

                for (int i = 0; i < nhosts; i++)
                {
                    hosts = (HOST*)realloc(hosts, nhosts * sizeof(HOST));
                    if(strstr(host_name_list[i], ":") != NULL)
                    {
                        // get custom port value
                        char *token = strtok(host_name_list[i], ":");
                        hosts[curr_host].name = (char*)malloc(sizeof(char));
                        hosts[curr_host].name = token;
                        token = strtok(NULL, ":");
                        cust_port = atoi(token);
                        hosts[curr_host].port = cust_port;
                    }
                    else
                    {
                        // default
                        hosts[curr_host].name = (char*)malloc(sizeof(char));
                        hosts[curr_host].name = host_name_list[i];
                        hosts[curr_host].port = default_port;
                        
                    }
                    printf("%s: %d\n", hosts[curr_host].name, hosts[curr_host].port);
                    curr_host++;
                }
            }

            if(strstr(line, "actionset") != NULL && line[0] != '\t')
            {
                num_sets++;
                sets = (ACTION_SET*)realloc(sets, num_sets * sizeof(ACTION_SET));
            }

			if (line[0] == '\t')
			{
                printf("Current set: %d, Number of sets: %d\n", curr_set+1, num_sets);

				if (line[1] == '\t') 
            	{
                    //num_sets++;
                    // take in actions by dividing the line 
                    curr_req = 0;
                    int nwords;
                    char **words = strsplit(line, &nwords);

                    for(int i = 0; i < nwords; ++i)
                    {
                        if(strcmp(words[i], "requires") == 0)
                        {
                            continue;
                        }
                        else
                        {
                            printf("Requirement: %s\n", words[i]);
                            sets[curr_set].actions[curr_action].num_req++;
                            printf("Realloc\n");
                            sets[curr_set].actions[curr_action].requirements = (char**) realloc(sets[curr_set].actions[curr_action].requirements, 
                                                                                       sets[curr_set].actions[curr_action].num_req * sizeof(char*));
                           
                            printf("Assign\n");
                            sets[curr_set].actions[curr_action].requirements[curr_req] = (char *)malloc(strlen(words[i]) * sizeof(char));
                            sets[curr_set].actions[curr_action].requirements[curr_req] = words[i];
                            printf("%s\n", sets[curr_set].actions[curr_action].requirements[curr_req]);
                            curr_req++;
                        }
                    }

                    curr_set++;
            	}
                else
                {
                    // take in actions

                    sets[curr_set].num_actions++;
                    sets[curr_set].actions = (ACTION*)realloc(sets[curr_set].actions, 
                                                              sets[curr_set].num_actions * sizeof(ACTION));
                    
                    int nwords = 0;
                    char **words = strsplit(line, &nwords);

                    char new_cmd[MAX_LINE_LENGTH] = "";
                    for (int i = 0; i < nwords; i++)
                    {
                        if(strstr(words[i], "remote-") != NULL)
                        {
                            sets[curr_set].actions[curr_action].is_remote = 1;
                            
                            remove_str(words[i], '-', new_cmd);
                            
                        }
                        else
                        {
                            strcat(new_cmd, words[i]);
                            strcat(new_cmd, " ");
                        }

                    }       
                    strcat(new_cmd, "\0");
                    sets[curr_set].actions[curr_action].command = (char*)malloc(MAX_LINE_LENGTH * sizeof(char));
                    sets[curr_set].actions[curr_action].command = new_cmd;
                    printf("%s", sets[curr_set].actions[curr_action].command);
                    curr_action++;
                    
			

                }
			}	

        }
    }

}

void perform_actions(ACTION_SET *sets)
{

    //ITERATE THROUGH THE ACTION SET
    for(int i = 0; i < num_sets; i++)
    {
        printf("Current set\n");
        ACTION_SET current_set = sets[i];
        printf("Getting actions\n");
        ACTION *current_actions = current_set.actions;

        printf("Iterating\n");
        printf("%d\n", sets[i].num_actions);
        for (int j = 0; j < sets[i].num_actions; j++)
        {
            printf("Current action\n");
            ACTION current_action = *current_actions; 
            printf("iterating req\n");
            for (int k = 0; k < current_action.num_req; k++)
            {
                printf("requirements\n");
                if(fopen(current_action.requirements[k], "r") == NULL)
                {
                    printf("Invalid\n");
                    break;
                }
            }
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

    ACTION_SET *sets = (ACTION_SET*)malloc(sizeof(ACTION_SET));
    HOST *hosts = (HOST*)malloc(sizeof(HOST));

    file_process(file_name, sets, hosts);
    perform_actions(sets);

    return 0; 
}