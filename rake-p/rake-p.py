import os
# Must find then read the Rakefile (txt file)
# Default: try and open and read from Rakefile in current directory or provide files location on rake client's command line.

# Find all matches for name Rakefile.txt

file = open('Rakefile', 'r')

array_actions = []

# content = file.readlines()
count = 0
for line in file.readlines():
    
    # print(line)
# print("Line{}: {}".format(count, line.split()))
    # Ignore lines starting with #
    if not (line.startswith('#')):
        # print("ignore line")

        # If line doesn't start with a space
        if  (line[0] == '\t'):
            count += 1

            print("Line{}: {}".format(count, line.split()))
            # Save the action sets in arrays
            # array_actions.append(line)
            # print(array_actions)

    # print(line[9])
    # begins with one tab = actions, create array with all lines with this (add to list)
    
    # if (line.startswith('\t')):
    #     # add string to array_actions
    #     # array_actions
    #     print('reached an action')
        


# print(file.read())

# Distinct type of lines (1. Empty lines with no tab Eg[PORT = 1234, or actionsetN])
#  (2. begins with one tab = actions)
#  (3. Lines that begin with two tabs = indicate which files are required for the previous action)

# Store the information from each line into scalar variables or arrays. 
# There is no sorting or fast-lookup required, so arrays, and arrays of arrays, will be sufficient. Distinguish between local and remote actions.
# Could use split() to break each line into words










# Finding all name
# def find_all(name, path):

#     os.path.dirname(os.path.dirname(path))
#     result = []
#     for root, dirs, files in os.walk(path):
#         if name in files:
#             result.append(os.path.join(root, name))
#     return result



# Additional Notes
#  Create an struct for hostname and port number

# Create an Array-Action, Array2 - remote, Array 3 - requires

