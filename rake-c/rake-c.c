#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

#define MAX_LINE_LENGTH 80

// struct for action?
typedef struct action
{
    bool is_remote;
    char *flags; 
    char *action; 

} ACTION;

ACTION *actions = (ACTION*)malloc(sizeof(ACTION));

void file_process(char *file_name)
{
    FILE *fp = fopen(file_name, "r");
    if(fp == NULL)
    {
        fprintf(stderr, "Invalid file\n");
    }
    else
    {
        char line[MAX_LINE_LENGTH] = "";
        int num_actions = 0;
        int curr_action = 0;
        char **actions = (char **)malloc(sizeof(char*));

        int num_req = 0;
        int curr_req = 0;
        char **requirements = (char**)malloc(sizeof(char*));

        // READ AND PARSE FILES LINE BY LINE
        while(fgets(line, MAX_LINE_LENGTH, fp))
        {
            if (line[0] == '#')
            {
                continue;
            }

			if (line[0] == '\t')
			{
				if (line[1] == '\t') 
            	{
                    // take in actions by dividing the line 
                    char *program = strtok(line, " ");

                    while(program != NULL)
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
                    }
            	}
                else
                {
                    // take in actions
                    num_actions++; 
                    actions = (char **)realloc(actions, num_actions * sizeof(char*));
                    actions[curr_action] = (char*)malloc(MAX_LINE_LENGTH * sizeof(char));
                    actions[curr_action] = line;
                    printf("%s\n", actions[curr_action]);
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