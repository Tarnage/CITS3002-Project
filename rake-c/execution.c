#include "execution.h"

int check_file_exists(char *filename)
{
    struct stat buffer;
    int exists = stat(filename, &buffer);
    
    if(exists == 0)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}

void perform_actions(ACTION_SET *action_set)
{
    printf("Number of sets: %d\n", num_sets);
    for (int i = 0; i < num_sets; i++)
    {
        printf("Number of actions: %d\n", action_set[i].action_totals);
        for (int j = 0; j < action_set[i].action_totals; j++)
        {
            for(int k = 0; k < ACTION_DATA(i, j).req_count; k++)
            {
                printf("Requirement: %s\n", ACTION_DATA(i, j).requirements[k]);
                if(check_file_exists(ACTION_DATA(i,j).requirements[k]) == 0)
                {
                    printf("%s\n", ACTION_DATA(i, j).requirements[k]);
                } 
            }

            int pid = fork();
            switch(pid)
            {
                case -1:
                    printf("fork() FAILED, EXITING");
                    exit(EXIT_FAILURE);
                case 0:
                    execl("/bin/sh/", ACTION_DATA(i,j).command);
            }
        }
    }
}