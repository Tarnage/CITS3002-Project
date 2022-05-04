import os
import re
import client_socket
file = open('Rakefile', 'r')

# Arrays
array_action_sets = []
# array_port_numbers = []
# array_host_names = []
# one_tab_numbers = []
# two_tab_numbers = []

one_tab_single_array = []

# Counters
count = 0
action_set_counter = 0
port_number_counter = 0
host_name_counter = 0


def cleanArray(input_array):
    print("One_Tab FIRST{}".format(input_array))
    # Remove double array created
    input_array = input_array[0]
    print("One_Tab Second{}".format(input_array))
    while("" in input_array):
        input_array.remove("")

    print("One_Tab{}".format(input_array))


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
            one_tab_array = line.split()
            # one_tab_split = re.split("[:\s]", line)
            # one_tab_numbers.append(one_tab_split)

            if(line[1] == 'r'):
                print("	One Tab (Remote){}: {}".format(count, one_tab_array))
            if(line[1] != 'r'):
                print("	One Tab (Client){}: {}".format(count, one_tab_array))

            # print("CleanOneTAB" + cleanArray(one_tab_numbers))

            #  2 tabs
        if (line[1] == '\t'):
            two_tab_array = line.split()
            # print("		Two Tabs-{}: {}".format(count, line.split()))
            # two_tab_split = re.split("[:\s]", line)
            # two_tab_numbers.append(two_tab_split)
            print("		Two Tabs-{}: {}".format(count, two_tab_array))
            # print("Two_Tab{}".format(two_tab_numbers))

        # Port and Hosts
        if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a'):
            # print("Port and Host-{}: {}".format(count, line.split()))

            # PortNumbers
            if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a' and line[0] == 'P'):
                port_number_array = line.split()
                # array_name_split = re.split("[:\s]", line)
                # array_port_numbers.append(array_name_split)
                print("PortNumbers{}".format(port_number_array))
                port_number_counter += 1

                # HostNames
            if(line[0] != '\t' and line[1] != '\t' and line[0] != 'a' and line[0] == 'H'):
                host_number_array = line.split()
                # host_name_split = re.split("[:\s]", line)
                # array_host_names.append(host_name_split)
                print("HostNames{}".format(host_number_array))
                host_name_counter += 1

        # ActionSets
        if(line[0] != '\t' and line[1] != '\t' and line[0] == 'a'):
            # print("Actionset-{}: {}".format(count, line.split()))
            array_action_sets.append(line)
            print("ActionSet!!!! {}".format(array_action_sets))
            action_set_counter += 1


# Save into array
	