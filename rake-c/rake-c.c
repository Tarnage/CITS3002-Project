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



void file_process(char *file_name)
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

        ACTION_SET *sets = (ACTION_SET*)malloc(sizeof(ACTION_SET));
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

				if (line[1] == '\t') 
            	{
                    // take in actions by dividing the line 
                    int nwords;
                    char **words = strsplit(line, &nwords);

                   /* while(program != NULL)
                    {
                        if(strstr(program, ".c") != NULL || 
                            strstr(program, ".h") != NULL ||
                            strstr(program, ".o") != NULL)
                            {
                                
                                num_req++;
                                requirements = (char **)realloc(requirements, num_req * sizeof(char*));
                                requirements[curr_req] = (char *)malloc(MAX_LINE_LENGTH * sizeof(char));
                                requirements[curr_req] = program;
                                printf("%s\n", requirements[curr_req]);
                                curr_req++;
                            }
                        program = strtok(NULL, " ");
                    }*/

                    for(int i = 0; i < nwords; ++i)
                    {
                        printf("Iterating through requirements\n");
                        if(strcmp(words[i], "requires") == 0)
                        {
                            printf("Word: %s\n", words[i]);
                        }
                        else
                        {
                            printf("Word: %s\n", words[i]);
                            sets->actions[curr_action].num_req++;
                            printf("Requirement incremented\n");
                            sets->actions[curr_action].requirements = (char**) realloc(sets->actions[curr_action].requirements, 
                                                                                        sets->actions[curr_action].num_req * sizeof(char*));
                            printf("Requirements array reallocated\n");
                            sets->actions[curr_action].requirements[curr_req] = (char *)malloc(MAX_LINE_LENGTH * sizeof(char));
                            printf("Allocated for current program\n");
                            sets->actions[curr_action].requirements[curr_req] = words[i];
                            printf("%s\n", sets->actions[curr_action].requirements[curr_req]);
                            ++curr_req;
                        }
                    }
            	}
                else
                {
                    // take in actions
                    /*num_actions++; 
                    actions = (char **)realloc(actions, num_actions * sizeof(char*));
                    actions[curr_action] = (char*)malloc(MAX_LINE_LENGTH * sizeof(char));
                    actions[curr_action] = line;
                    printf("%s\n", actions[curr_action]);
                    curr_action++; */

                    sets[curr_set].num_actions++;
                    sets[curr_set].actions = (ACTION*)realloc(sets[curr_set].actions, 
                                                              sets[curr_set].num_actions * sizeof(ACTION));
                    
                    int nwords = 0;
                    char **words = strsplit(line, &nwords);
                    for (int i = 0; i < nwords; i++)
                    {
                        if(strstr(words[i], "remote-"))
                        {
                            sets[curr_set].actions[curr_action].is_remote = 1;
                        }
                    }

                    sets[curr_set].actions[curr_action].command = (char*)malloc(MAX_LINE_LENGTH * sizeof(char));
                    sets[curr_set].actions[curr_action].command = line;
                    printf("%s\n", sets[curr_set].actions[curr_action].command);
                    curr_action++;

                }
			
			}		
        }
    }

}

int main (int argc, char *argv[])
{
    char* file_name = argv[1];
    file_process(file_name);

    return 0; 
}