#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <ctype.h>
#include "strsplit.c"

#define MAX_LINE_LENGTH 80

// STRUCT FOR ACTION AND ACTION SETS
typedef struct action
{
    int is_remote;
    char *command; 
    int num_req;
    char **requirements; 

} ACTION;

typedef struct action_set
{
    int num_actions;
    ACTION *actions; 
} ACTION_SET;

void remove_str(char *line, char *intended)
{
    int counter_line = 0;
    int new_word_counter = 0;


    while(line[counter_line] != '-')
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

void file_process(char *file_name, ACTION_SET *sets)
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
        // char **actions = (char **)malloc(sizeof(char*));

        int curr_req = 0;
        int num_sets;

        // ACTION_SET *sets = (ACTION_SET*)malloc(sizeof(ACTION_SET));
        sets[curr_set].num_actions = 0;
        sets[curr_set].actions = (ACTION*)malloc(sizeof(ACTION));
        sets[curr_set].actions[curr_action].requirements = (char**)malloc(sizeof(char*));
        sets[curr_set].actions[curr_action].num_req = 0;

        char line[MAX_LINE_LENGTH] = "";
        

        // READ AND PARSE FILES LINE BY LINE
        while(fgets(line, MAX_LINE_LENGTH, fp))
        {
            if (line[0] == '#')
            {
                continue;
            }

			if (line[0] == '\t')
			{
                num_sets++;
                sets = (ACTION_SET*)realloc(sets, num_sets * sizeof(ACTION_SET));
                curr_action = 0;

				if (line[1] == '\t') 
            	{
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
                            sets->actions[curr_action].num_req++;
                            sets->actions[curr_action].requirements = (char**) realloc(sets->actions[curr_action].requirements, 
                                                                                       sets->actions[curr_action].num_req * sizeof(char*));
                           
                            sets->actions[curr_action].requirements[curr_req] = (char *)malloc(MAX_LINE_LENGTH * sizeof(char));
                            sets->actions[curr_action].requirements[curr_req] = words[i];
                            printf("%s\n", sets->actions[curr_action].requirements[curr_req]);
                            ++curr_req;
                        }
                    }
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
                            
                            remove_str(words[i], new_cmd);
                            
                        }
                        else
                        {
                            strcat(new_cmd, words[i]);
                            strcat(new_cmd, " ");
                        }

                    }       
                    
                    //printf("%s", new_cmd);
                    sets[curr_set].actions[curr_action].command = (char*)malloc(MAX_LINE_LENGTH * sizeof(char));
                    sets[curr_set].actions[curr_action].command = new_cmd;
                    printf("%s", sets[curr_set].actions[curr_action].command);
                    curr_action++;

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
    
    file_process(file_name, sets);

    return 0; 
}