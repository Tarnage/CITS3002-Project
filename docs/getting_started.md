# Practical CITS3002 project 2022 - getting started
## **Author** [Chris McDonald](https://research-repository.uwa.edu.au/en/persons/chris-mcdonald)

Like many large, frightening projects this one can be considerably simplified by breaking the project down into smaller steps and stages - problem decomposition. None of this is specific to Computer Networks, it's better described as the 'common-sense' part of Software Engineering.

The following steps should assist you in deciding how to break down the problem. They haven't been followed specifically in this order to build a sample solution, though they should 'work' to build a solution. Note - this is not the only way to implement a solution.

The steps have not been written so that multiple people in a team can 'go away and come back' with their part completed. Instead it is strongly suggested that members of a team work together, because multiple parts of the project, and their interactions, need testing at the same time. Moreover, it's important that all team members understand how their whole project works, and not just the part that they developed. 

#

- **rake client locates, opens, and parses Rakefile**

    The client runs on your desktop or laptop computer. You need to develop two independent rake clients, one in C and one in Python, but you should first develop one client and your rakeserver, before developing your second client. Your two clients, despite being implemented in different programming languages, will be using the same protocol (your protocol), to communicate with your rakeserver.

    Each rake client needs to find and read the Rakefile (a textfile) to determine what actions need to be performed, and where. By default each rake client should just try to open and read from Rakefile in the current directory, or (optionally) you may wish to provide the file's location on the rake client's command-line.

    Open and read the textfile line-by-line. Firstly remove/ignore everything after the comment symbol '#'. There are only a few distinct types of lines - empty lines; lines that don't begin with a tab - (of the form PORT = 1234, or actionsetN:) ; lines that begin with one tab, which are actions; lines that begin with two tabs, indicating which files are required for the previous action.
    Store the information from each line into scalar variables or arrays. There is no sorting or fast-lookup required, so arrays, and arrays of arrays, will be sufficient. Distinguish between local and remote actions.

    You will find it helpful to break each line into 'words'. Python has a simple method split() to do this, and here's a similar C99 function: strsplit.zip. 

# 

- **execute all actions on the rake client's computer**

    While you may not use this code/approach at the end, have your rake client program execute all actions on your client's computer. Start by using a very simple Rakefile - just a single actionset (initially of just one command), and no remote execution - don't have any remote-XX actions. The action can be very simple - it does not have involve compilation or linking. This step will require you to implement code to invoke/execute a new external process (on the current computer), wait for it to finish, and capture/use its exit status.

    Some actions will produce output. Where will the output go? How are you going to obtain/capture/access and report their output? Actions may also fail, and may report that failure in different ways to different 'locations'. Ensure that you can detect an action that has failed, and consider how you are going to obtain/capture/access and report its failure.

    Next, support the invocation/execution of multiple actions by the rake client, on the client's computer. Initially, just execute each action individually, sequentially, waiting for each action to finish (successfully), before starting the next.

    Finally, add a second and a third actionset, and have each of them execute on the client's computer. Each actionset (in whole) must execute successfully before the next actionset is commenced.

#

- <del>**commence development and testing of your rakeserver**</del>

    In practice your rakeserver will need to be executing, and awaiting new network connections, before any rake clients can connect to it. Your rakeserver doesn't require command-line arguments, doesn't read the Rakefile, or have access to the source and object files it needs work with (though it may have its own special libraries used in final linking).

    Firstly, have your rakeserver create a socket, bind() a pre-defined or operating-system-allocated port number to the socket, print 'listening on port XXXX', and call accept() to block and wait for an incoming rake client. Unless your rakeserver's port is hard-coded into its source-code, you'll need to modify your client's Rakefile to indicate which port the server is listening on.

    Initially, execute your rakeserver on the same computer as the client, and use the hostname localhost in the Rakefile to specify its location. You can have multiple instances of your rakeserver running on each host, including localhost, but each will need to be listening on a distinct port number.

    You can initially test connectivity from your client's computer to your rakeserver with the command: 

    ```console
    prompt> nc  servers-hostname  serversport-number
    ```
    e.g.
    ```console
    prompt> nc  localhost  12345 
    ```

    Have your rakeserver print out a message (to the screen) when a new client connection is accepted.

    Next, we'll send a line of text to the rakeserver. Have your rakeserver print the received text to the screen: 

    ```console
    prompt> echo CITS3002 | nc  localhost  12345 
    ```

    Next, change your rakeserver so that it writes the received text back to the nc command, and redirect the returned line of text to a new file so that we don't confuse the result with any printing to the screen: 

    ```console
    prompt> echo CITS3002 | nc  localhost  12345 > filename
    prompt> cat  filename 
    ```

#

- <del>**extending your rake client to contact your rakeserver**</del>

    At this point you should have a nearly complete rake client, that reads and stores the contents of a Rakefile, executes actions (locally), captures and report actions' output, and performs correctly based on whether the action(s) were successful or otherwise.

    We next want to perform the actions of the nc command using our rake client. Our rake client needs to allocate a socket, and connect to an already running rakeserver. Initially, just hardcode the network name or address, and port-number of your server into your client's code, but eventually replace these with information read and stored from your Rakefile.

    Once your rake client connects to your server, have the client write a line of text to the server, and have the server read and return (write back) the same line of text to the client, printing as much 'debug' information to the screen to demonstrate that it's working. Initially, run your rakeserver on the client's computer (localhost), but then move/copy your rakeserver to a physically different computer, and ensure that your rake client can contact it and exchange a line of text. 

#

- **supporting multiple instances of your rakeserver**

    Next - getting more difficult - modify your rake client so that it can simultaneously manage connections to two different instances of your rakeserver. Write a different line of text to each server, have each server echo the text back to the (same) rake client, and display the output to the screen.

    Now, have each rakeserver sleep for a random period of time before echoing its text string - in C: 
    
    ```c
    sleep( getpid() % 5 + 2);
    ```

    Run your rake client a few times to ensure that you observe a good 'mix' of random delays, and have your rake client display (to the screen) whichever response arrives first. This is where it gets tricky - your client should be willing to receive the reply from either remote server, and in any order, initially from just two servers but eventually from 10+.

    Your first reaction may be to want to use threads in C and Python to address this challenge, but the very strong recommendation is read about the system-call and function named select(), available in both languages.

#

- **exchange meaningful commands and responses**

    Now that your clients and servers are communicating successfully with meaningless lines of text, we'll send and respond with structured commands and responses. It's the role of your client to instruct your server(s), and the servers' role to perform and respond to those instructions.

    In the first instance, have your client ask each server the cost of executing a command. The server should determine its 'price' (based on what command is to be performed, what resources are required, and how busy the server is), and respond with that value. The client chooses the server making the lowest 'bid', and will then (next) ask that server to execute the command. The client's request for a cost, and each servers' response, form the first meaningful exchange, and are the first two 'types' of message in your project's protocol.

#

- **execute simple actions on your rakeserver**

    Getting close! You have already developed code to have your rake client execute processes on its local computer. The same code now needs copying into your rakeserver's code, so that actions may be executed on remote hosts. Which actions? The ones specified in the client's Rakefile, and sent from the client to each rakeserver as a line of text.

    Initially, only send and execute simple actions that don't require any additional files. Two very important considerations at this point - each rakeserver will be executing on a different, remote, computer, possibly in another room, or another country. So you won't be able to see any command's output appear on remote screens. How are you going to see that output? And, how is the rakeserver going to inform the rake client that the remote execution was successful, or not? 

#

- **performing compilation and linking**

    To date we've only been executing simple actions with our rakeserver, capturing their output and exit status, and returning that to the requesting client.

    Compilation and linking are examples of more complex actions that require additional files from the client and, possibly, need to return files to the client. Lines in each Rakefile indicate if an action requires one or more input files before the action can be commenced. These files (only) exist on the client's host, and each needs sending to the rakeserver. Note that some required files will be textfiles (such a C source code required for compilation), but others may be 'binary files' (such as object files required for linking).

    Successful compilation and linking actions will produce an output file, typically a 'binary' object file or an executable file. You may assume that just one output file is produced for each action. How will you determine if, and what, output files have been produced? How will your rakeserver inform the client of the name of the output file, and how will the rakeserver send the file back?

#

- **more to come**
    There is always more to come. 