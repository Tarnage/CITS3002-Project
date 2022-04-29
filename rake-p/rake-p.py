import os

file = open('Rakefile', 'r')

array_actions = []

count = 0
for line in file.readlines():

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
            print("Port and Host-{}: {}".format(count, line.split()))

        if(line[0] != '\t' and line[1] != '\t' and line[0] == 'a'):
            print("Actionset-{}: {}".format(count, line.split()))
