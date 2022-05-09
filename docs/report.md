# Rake Server and Client

## Introduction
### Explain Motivation
Whats the problem we are trying to solve and why

## Technology Involved
### Explain why we are using TCP/IP over LAN opposed to UDP or HTTML

## Desgin
## Why we would use a simplex connectionless service also known as unacknowledged connectionless service. compared to the others

## Good read about how to allocate buffer size
## https://stackoverflow.com/questions/2811006/what-is-a-good-buffer-size-for-socket-programming


## Explain that we will use the finite state machine(FSMs) concept where the conenctions are individual FSMs 

## Explain the protocol our program will use
## Should use fixed byte order instead of below
## https://stackoverflow.com/questions/52722787/problem-sending-binary-files-via-sockets-python


when the client sends a request, the datagram must be in the form of a number representing how to deal with the payload a space and the payload, if any. Clients will send a byte stream when decoded will look something like this

$sigma$ $d$

7 [FILENAME]

8 [FILESIZE]

9 [FILE CONTENTS]

where $sigma$ is the transition and $d$ is the payload, seperated by a space, (can be single can be more). $sigma$ will indicate what state the connection has to be in to process the payload otherwise the connection will be in an error state which should be reported and exited gracefully.

