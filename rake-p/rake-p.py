import os
import re

file = open('Rakefile', 'r')

# Arrays
array_action_sets = []
array_port_numbers = []
array_host_names = []

# Counters
count = 0
action_set_counter = 0
port_number_counter = 0
host_name_counter = 0

for line in file.readlines():
    # with open('Rakefile') as file:

    if not (line.startswith('#')):
        count += 1

        # Remove blank lines (Removes string index error when calling line[1])
        if not line.strip():
            continue

            # 1 tab
        if (line[0] == '\t' and line[1] != '\t'):
            print("	One Tab{}: {}".format(count, line.split()))

            #  2 tabs
        if (line[1] == '\t'):
            print("		Two Tabs-{}: {}".format(count, line.split()))

        # Port and Hosts
        if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a'):
            # print("Port and Host-{}: {}".format(count, line.split()))

            # PortNumbers
            if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a' and line[0] == 'P'):
                array_port_numbers.append(line)
                print("PortNumbers{}".format(array_port_numbers))
                port_number_counter += 1

                # HostNames
            if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a' and line[0] == 'H'):
                host_name_split = re.split("[:\s]", line)
                array_host_names.append(host_name_split)
                print("HostNames{}".format(array_host_names))
                host_name_counter += 1

        # ActionSets
        if(line[0] != '\t' and line[1] != '\t' and line[0] == 'a'):
            # print("Actionset-{}: {}".format(count, line.split()))
            array_action_sets.append(line)
            print("ActionSet!!!! {}".format(array_action_sets))
            action_set_counter += 1
