#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LENGTH 80

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
        int action_counter; 
        char **actions = (char **)malloc(sizeof(char*));

        // READ AND PARSE FILES LINE BY LINE
        while(fgets(line, MAX_LINE_LENGTH, fp))
        {
            if (line[0] == '#')
            {
                continue;
            }

			if (line[0] == '\t')
			{
                // take in actions
                num_actions++; 
                actions = (char **)realloc(actions, num_actions * sizeof(char*));
                actions[curr_action] = (char*)malloc(MAX_LINE_LENGTH * sizeof(char));
                actions[curr_action] = line;
                printf("%s\n", actions[curr_action]);
                curr_action++; 

				if (line[1] == '\t') 
            	{
					printf("Req prog\n");

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