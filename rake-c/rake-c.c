#include "rake-c.h"

#define MAX_LINE_LENGTH 80

ACTION**    action_set  =   NULL;
HOST*       hosts       =   NULL;
int         num_hosts   =   0;

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

void file_process(char *file_name)
{
    FILE *fp = fopen(file_name, "r");
    if(fp == NULL)
    {
        fprintf(stderr, "Invalid file\n");
    }
    else
    {
        // LINE VARIABLE FOR READING
        char line[MAX_LINE_LENGTH] = "";

        // DEFAULT PORT
        int default_port; 

        // THE CURRENT SET
        int current_set;

        // THE CURRENT ACTION
        int current_action;

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
                char port_val[MAX_LINE_LENGTH] = "";
                remove_str(line, '=', port_val);

                default_port = atoi(port_val);
                
            }
            // CHECK IF THE LINE GIVES THE HOST NAMES
            else if(strstr(line, "HOSTS") != NULL)
            {
                int nhosts;
                char host_names[MAX_LINE_LENGTH] = "";
                remove_str(line, '=', host_names);
                char **host_name_list = strsplit(host_names, &nhosts);

                for (int i = 0; i < nhosts; i++)
                {
                    
                    hosts = (HOST*)realloc(hosts, nhosts * sizeof(HOST));
                    // CHECK IF HOST NAME HAS ASSOCIATED PORT
                    if(strstr(host_name_list[i], ":") != NULL)
                    {
                        // SPLIT THE LINE BY THE DELIMITER ":"
                        char *token = strtok(host_name_list[i], ":");
                        
                        hosts[num_hosts].name = (char*)malloc(sizeof(char));
                        hosts[num_hosts].name = token;
                        
                        token = strtok(NULL, ":");
                        
                        int cust_port = atoi(token);
                        hosts[num_hosts].port = cust_port;
                    }
                    else
                    {
                        // default
                        hosts[num_hosts].name = (char*)malloc(sizeof(char));
                        hosts[num_hosts].name = host_name_list[i];
                        hosts[num_hosts].port = default_port;
                        
                    }
                    printf("%s: %d\n", hosts[num_hosts].name, hosts[num_hosts].port);
                    num_hosts++;
                    printf("Hosts found: %d\n", num_hosts);
                }
            } 
            // CHECK IF THE LINE IS INDICATING AN INCOMING ACTION SET
            else if (strstr(line, "actionset") != NULL  && line[0] != '\t')
            {
                // INCREMENT THE NUMBER OF ACTION SETS
                num_sets++;
                // ALLOCATE MEMORY TO A NEW ACTION SET
                action_set = (ACTION**)realloc(action_set, num_sets * sizeof(ACTION*));
                
                current_set = num_sets - 1;
                // SET THE NUMBER OF ACTIONS FOR THIS ACTION SET TO ZERO
                num_actions = 0;
            }
            // CHECK IF IT IS EITHER AN ACTION OR A LIST OF REQUIREMENTS
			else if (line[0] == '\t')
			{
                // CHECK IF REQUIREMENT
				if (line[1] == '\t') 
            	{
                    int num_req;
                    int curr_req; 
                    int nwords;
                    char **words = strsplit(line, &nwords);

                    printf("Requires: ");
                    for(int i = 0; i < nwords; ++i)
                    {
                        // IF THE WORD CONTAINS "REQUIRES"
                        if(strcmp(words[i], "requires") == 0)
                        {
                            continue;
                        }
                        else
                        {
                            num_req++;
                            action_set[current_set][current_action].requirements = (char**)realloc(action_set[current_set][current_action].requirements, num_req * sizeof(char*));
                            action_set[current_set][current_action].requirements[curr_req] = (char *)malloc(strlen(words[i]) * sizeof(char));
                            action_set[current_set][current_action].requirements[curr_req] = words[i];
                            printf("%s ", action_set[current_set][current_action].requirements[curr_req]);
                            curr_req++;
                        }
                    }
                    curr_req = 0;
                    num_req = 0;
                    printf("\n");
            	}
                // OTHERWISE, ACTION
                else
                {
                    num_actions++;
                    current_action = num_actions - 1;
                    // ALLOCATE MEMORY TO THE ACTION
                    action_set[current_set] = (ACTION*)realloc(action_set[current_set], num_actions * sizeof(ACTION));
                    
                    int nwords = 0;
                    char **words = strsplit(line, &nwords);

                    char new_cmd[MAX_LINE_LENGTH] = "";
                    for (int i = 0; i < nwords; i++)
                    {
                        if(strstr(words[i], "remote-") != NULL)
                        {
                            action_set[current_set][current_action].is_remote = 1;
                            
                            remove_str(words[i], '-', new_cmd);
                            
                        }
                        else
                        {
                            strcat(new_cmd, words[i]);
                            strcat(new_cmd, " ");
                        }

                    }       
                    strcat(new_cmd, "\0");
                    action_set[current_set][current_action].command = (char*)malloc(strlen(new_cmd) * sizeof(char));
                    action_set[current_set][current_action].command = new_cmd;
                    printf("%s", action_set[current_set][current_action].command);

                }
			}	
        }
    }

}


void perform_actions()
{
    // ITERATE THROUGH THE ACTION SETS

    for(int i = 0; i < num_sets; i++)
    {
        printf("%s\n", action_set[i][0].command);
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
    

    file_process(file_name);
    
    perform_actions();

    return 0; 
}