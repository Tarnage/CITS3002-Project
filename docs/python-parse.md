# parse_rakefile

## Using parse_rakefile module

Simply import the module to the main file you wish to invoke the modules

```python
import parse_rakefile
```

### parse_rakefile.**read_rake**(filename)
Locates the Rake file by the filename argument given.

Returns a tuple, a dictionary of key=hosts and value=ports and a data structure of the file. The data structure will be described from the outter most to inner most. The data structure will return a list that contains, a list of actions Action objects

for example, When you iterate the outter most list it will return a list of actionset1, actionset2, actionset3, etc..

When you iterate each of these lists, actionset1 for example, it will return Action objects (in order of execution) that contain 3 member variables to track what and how the commands need to be executed. Please see below for details of the Action object.


Example:
```python
    (hosts, actions) = parse_rakefile.read_rake(filename)

    # To access hosts
    for key in hosts:
        print(key, hosts[key])
    # prints "hostname 6328"
    # where key is a string and hosts[key] returns an int

    # To access actions
    # where actions = [sets1, sets2, sets3, ...]
    # and sets      = [command1, command2, ...]
    # and command = is an Action object with memember variables, [cmd, remote, requires] 
    for sets in actions:
        for command in sets:
            if not command.remote:
                # do command locally
                print(command.remote)
                # prints False
                print(command.cmd)
                # prints command line argument i.e.
                # echo starting actionset1
                print(command.requires)
                # returns a list of strings i.e.
                # [program.c program.h allfunctions.h]
            else:
                # send command to server to execute
```

## Action Object

```python
class Action:
	def __init__(self, cmd, remote, requires):
		'''
			Args:
				cmd (str): command line to execute
				remote (boolean): run cmd local or remote
				requires (list): list of strings required to execute cmd 
		'''
		self.cmd = cmd
		self.remote = remote
		self.requires = requires
```

Straight forward class, just has public member variables for now.

Each object(command) in sets is a new instance of this class.


```Ruby
    PORT  = 6238
    HOSTS = hostname1 hostname2 hostname3:6333

    actionset1:
        echo starting actionset1
        remote-cc [optional-flags] -c program.c
            requires program.c program.h allfunctions.h
        remote-cc [optional-flags] -c square.c
            requires square.c allfunctions.h
        remote-cc [optional-flags] -c cube.c
            requires cube.c allfunctions.h

    actionset2:
        echo starting actionset2
        remote-cc [optional-flags] -o program program.o square.o cube.o
            requires program.o square.o cube.o
```


[](data-structure.png)