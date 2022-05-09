#include "rake-c.h"

void perform_actions(ACTION_SET *action_set)
{
    printf("Number of sets: %d\n", num_sets);
    for (int i = 0; i < num_sets; i++)
    {
        printf("Number of actions: %d\n", action_set[i].action_totals);
        for (int j = 0; j < action_set[i].action_totals; j++)
        {
            
            printf("%s\n", ACTION_DATA(i, j).command);
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
    

    file_process(file_name, action_set, hosts);
    
    print_hosts(hosts);
    print_action_sets(action_set);

    perform_actions(action_set);

    return 0; 
}