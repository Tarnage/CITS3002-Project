#include "rake-c.h"



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
    
    // print_hosts(hosts);
    // print_action_sets(action_set);

    perform_actions(action_set);

    return 0; 
}
