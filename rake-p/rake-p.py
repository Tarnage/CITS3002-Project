import os
import re
import client_socket
file = open('Rakefile', 'r')

# Arrays
array_action_sets = []
array_actions = []
array_required = []

# Counters
count = 0
action_set_counter = 0
port_number_counter = 0
host_name_counter = 0
action_n_counter = 0

for line in file.readlines():
    # with open('Rakefile') as file:

    if not (line.startswith('#')):
        count += 1
        print(count)

        # Remove blank lines (Removes string index error when calling line[1])
        if not line.strip():
            continue

            # 1 tab
        if (line[0] == '\t' and line[1] != '\t'):

            #  Distinguish between actionsets by using if(== 'echo')
            one_tab_array = line.split()

            array_actions.append(one_tab_array)
            # print("	One Tab{}: {}\n".format(count, array_actions))

            #  2 tabs
        if (line[1] == '\t'):
            two_tab_array = line.split()
            array_required.append(two_tab_array)

            print("		Two Tabs{}: {}".format(count, array_required))

        # Port and Hosts
        if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a'):

            # PortNumbers
            if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a' and line[0] == 'P'):
                port_number_array = line.split()
                print("PortNumbers{}".format(port_number_array))
                port_number_counter += 1

                # HostNames
            if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a' and line[0] == 'H'):
                host_number_array = line.split()
                print("HostNames{}".format(host_number_array))
                host_name_counter += 1

        # ActionSets
        if(line[0] != '\t' and line[1] != '\t' and line[0] == 'a'):
            array_action_sets.append(line)
            print("ActionSet!!!! {}".format(array_action_sets))
            action_set_counter += 1


# Save into arrays
# print("array_actions: {}".format(array_actions))

for i in range(len(array_action_sets)):
    array_action_sets[i] = array_actions
