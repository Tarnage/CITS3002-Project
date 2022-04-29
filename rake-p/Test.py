
array = []
with open('Rakefile') as file:
    for line in file:
        array = [line.split()]
        print(("ActionSet!!!! {}".format(array)))
# print(line.rstrip())
