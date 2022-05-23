# Rake Server and Client

## Introduction
### Explain Motivation
This project aims to execute multiple instance of server programs on distinct (physical) computers connected using internet protocols, and each of the client programs on the computer. Implementation should not employ specific 3rd party frameworks or resources. Instead opting to use core networking functions such as (classes, methods, libraries,...) of each programming language. 

#

## Technology Involved
### Explain why we are using TCP/IP over LAN opposed to UDP or HTTP
TCP is slower but more reliable than UDP in the transference of data. TCP/IP protocol gurantees the delivery of data to the destination router with features such as deilvery acknowledgements, retransmissions, delay transmissions when the network is congested and easy error detection. The TCP/IP model also has a easier to scale client-server architecture that supports several routing protocols. (refer to diagram for example of why we require delivery acknowledgemnts)
#

#### Good read about how to allocate buffer size
#### https://stackoverflow.com/questions/2811006/what-is-a-good-buffer-size-for-socket-programming

#### Explain that we will use the finite state machine(FSMs) concept where the conenctions are individual FSMs 

#### Explain the protocol our program will use
#### https://stackoverflow.com/questions/52722787/problem-sending-binary-files-via-sockets-python

#

## Design
## Why we would use a simplex connectionless service also known as unacknowledged connectionless service. compared to the others
We are using a half-duplex method but dont have timeouts and we dont read msgs. Its kind of a cross between simplex and half-duplex, since connection over LAN is reliable and we cant have a timeout since compile files takes an unknown amount of time. Best we can do is just wait for an acknowledgement, or wait until an error message is sent. (But you may have a good idea)

### Protocol

When communications are made between client and server, the client must make the initial connection, the first type of communication must be represented as an 8 byte integer followed by any number of payloads. Once the entire datagram is sent by the client, the client will be in wait mode, until an acknowledgement has been recieved from the server, then more datagrams can be sent, in the same order of an 8 byte integer followed by one or more payloads. 

The 4 byte integer will prompt the server or the client what kind of payload to expect, this will set the receiving connection into a state in which it can properly accept the incoming payload. 

### Encoding type

Integers will be encoded into 8 bytes using the big edian byte order, where the most significant bytes will be stored first, at the lowest storage address.

Strings will be endoded using the utf-8 standard, 

For thought...
actually maybe just do everything in bytes.
We would have to send the size of the payload after ever type of communication followed by the size of payload then the payload.


### Walkthrough the program

1. Request for cost

2. Pick the server

3. Start sending files
    1. Client first sends filename and size
    2. Server receiving and writing txt files
    3. Once all files are sent the client will send the execute command
    4. Server will execute the command sent, and the reuturn status will be sent to the client. If the return staus is zero the server will initiate the protocol to send the output file, otherwise it will return the error message from executing the command.
    5. Sending the output file, since the output file 

<<<<<<< Updated upstream
=======
---------------------

### Walkthrough of server and client interactions
(Mention functions being called and what it returns
just follow one socket and its journey
first do just the client
then do the server)

1. Servers are created by running (python3 rakeserver.py 6328). Opening an port based on the command line third argument and listens for connections on that port number and IP address.

2. Client is created by running (python3 rake-p.py Rakefile). Client creates a connection to a given host on a given port given to the function create_socket as an parameter. Client then connects the socket and returns the connection object in the create_sock function for quote while listening for servers. 

3. When connection is established with an server the client will initate the connection by sending a preamble represented in 4 bytes and in edian byte order (CMD_QUOTE_REQUEST). 

4. The server that is waiting for this preamble recieves (CMD_QUOTE_REQUEST) and sends back an preamble (CMD_QUOTE_REPLY). If the preamble is not correctly converted on the client side the server will not be able to recognize the preamble and thus do nothing. 

5. The client waiting for an reply recieves the preamble (CMD_QUOTE_REPLY) amd waits for an second reply of the cost in edian byte order. Server sends cost and closes the connection, client recieves the cost and closes the connection. 

6. Steps 3 to 5 are repeated until the client has found server with lowest cost. 

7. Client creates and connects sockets for executing commands on the server with lowest cost. Client determines if it requires files by reading the Rakefile. If it does require files, client sends required files to the server by sending an preamble (CMD_SEND_FILE) in big edian byte order. 

8. Client will return code status detailing if there was an error or sucess when executing commands. On success the server will send a file and the client will receive the output file from command. If it was an error, client will output an error message and exit the program immediately. The execution of commands process is shown in the diagram (execute-cmd-protocol.png). 

>>>>>>> Stashed changes
## Performance
### conditions under which remote compliation and linking appears to perform better (faster) than just using your local machine

## Observations and improvements

## Conclusion