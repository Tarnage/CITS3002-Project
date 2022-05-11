
# Python3 code to demonstrate
# removing empty strings
# using remove()
testList2 = []
# initializing list
test_list = [['', 'echo', 'starting', 'actionset1', '']]
# testList2 = testList2.append(str(test_list[0]))
test_list = test_list[0]

print("YES : " + str(test_list))
# Printing original list
# print("Original list is : " + str(testList2))

# using remove() to
# perform removal
while("" in test_list):
    test_list.remove("")


# # Printing modified list
print("Modified list is : " + str(test_list))
