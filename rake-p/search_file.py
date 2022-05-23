#!/usr/bin/env python3

import os
from pathlib import Path
import time

def find_files(filename):
    result = None
    start = time.time()
# Walking top-down from the root
    for root, dir, files in os.walk("/"):
        if filename in files:
            result = (os.path.join(root, filename))
            break
    finish = time.time()
    print(finish - start)
    return result

result = find_files("doesnt_exist")

print(result == None)

def find(file_name):
    start = time.time()
    search_path = Path("/")
    for file in search_path.glob("**/*"):
        if file.name == file_name:
                print(f'file found = {file.absolute()}')
                finish = time.time()
                print(finish - start)
                break

#find("program.c")