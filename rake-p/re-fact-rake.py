#!/usr/bin/env python3

import parse_rakefile
from parse_rakefile import Action
import sys
import socket
import select
import subprocess
import os
import time
import random

# DEFAULT PORT AND HOSTS
SERVER_PORT 	= 50009
#SERVER_HOST = '192.168.1.105'
SERVER_HOST 	= '127.0.0.1'
LOCAL_HOST 		= '127.0.0.1'
# MAX SIZE OF BLOCKS WHEN READING IN STREAM DATA
MAX_BYTES 		= 1024
# THE STANDARD THIS PROGRAM WILL USE TO ENCODE AND DECODE STRINGS
FORMAT 			= 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
TIMEOUT 		= 5
# INTS OR ACKS ARE 8 BYTES LONG
MAX_BYTE_SIGMA 	= 4
# USE BIG BIG_EDIAN FOR BYTE ORDER
BIG_EDIAN 		= 'big'
# LOCATION OF RECV FILES
DOWNLOADS 		= "./downloads"

MAX_INT 		= sys.maxsize


class Ack:
    ''' ENUM  Class'''
    def __init__(self):
        self.CMD_ECHO = 0
        self.CMD_ECHOREPLY = 1

        self.CMD_QUOTE_REQUEST = 2
        self.CMD_QUOTE_REPLY = 3

        self.CMD_SEND_REQIUREMENTS = 4
        self.CMD_BIN_FILE = 5
        self.CMD_SEND_FILE = 6
        self.CMD_SEND_SIZE = 7
        self.CMD_SEND_NAME = 8

        self.CMD_EXECUTE_REQ = 9
        self.CMD_EXECUTE = 10
        self.CMD_RETURN_STATUS  = 11

        self.CMD_RETURN_STDOUT  = 12
        self.CMD_RETURN_STDERR  = 13

        self.CMD_RETURN_FILE = 14

        self.CMD_ACK = 15
        self.CMD_NO_OUTPUT = 16



class Connection:
    def __init__(self, ip: str, port: int, used: bool, action: Action, cost: int, got_cost: bool, is_local: bool, current_ack: int):
        self.ip = ip
        self.port = port
        self.used = used
        self.action = action
        self.cost = cost
        self.got_cost = got_cost
        self.is_local = is_local
        self.current_ack = current_ack

        self.sockfd = -1
        self.ACK = Ack()


    def connect(self) -> int:
        '''requests connection to the server and returns the fileno of the socket'''
        try:
            self.sockfd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.sockfd.connect( (self.ip, self.port) )
        except socket.error as err:
            if err.errno == 111:
                sys.exit( ( f'Connection refused with error: {err}' ) )
            else: 
                sys.exit( f'socket creation failed with error: {err}' )

        return self.sockfd.fileno()

    
    def disconnect(self):
        self.sockfd.shutdown(socket.SHUT_RDWR)
        self.sockfd.close()
        self.sockfd = -1


    def add_actions(self, actions: Action):
        self.actions = actions



def create_quote_team(hosts: dict) -> dict:
    '''returns a dictionary of fileno -> Connection Object'''

    slaves = dict()

    for ip in hosts:
        port = hosts[ip]
        try:
            sd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            #print( f"Socket succesfully created! ({host}:{port})" )
            #print( f'connecting to {host}:{port}...' )
            sd.connect( (ip, port) )
            
        except socket.error as err:
            if err.errno == 111:
                sys.exit( ( f'Connection refused with error: {err}' ) )
            else: 
                sys.exit( f'socket creation failed with error: {err}' )

        fileno = sd.fileno()
        slaves[fileno] = sd

    return slaves


def create_local_host() -> Connection:
    '''Helper to create the local host connection'''
    default_port = parse_rakefile.get_default_port()
    return Connection(LOCAL_HOST, default_port, used=True, action=None, cost=MAX_INT, got_cost=False, is_local=True, current_ack=-1)




def handle_conn(sets: list, hosts: dict):

    input_sockets = list()
    output_sockets = list()

    # conn_dict KEY=fileno, VALUE=Connection Object
    conn_dict = dict()


    local_host = create_local_host()


    actions_exe = 0
    curr_action = 0
    remaing_actions = len(sets)

    quote_queue = dict()
    
    while actions_exe < remaing_actions:
        try:
            if curr_action < remaing_actions:
                
                # IF ITS A LOCAL CMD USE LOCAL HOST OBJ
                if not sets[curr_action].remote:
                    local_host.add_actions(sets[curr_action])
                    fileno = local_host.connect()
                    conn_dict[fileno] = local_host
                    output_sockets.append(fileno)
                    curr_action += 1

                if curr_action < remaing_actions:
                    quote_queue = create_quote_team(hosts)

        except KeyboardInterrupt:
            sys.exit(1)
    
    pass



def main(argv):
    dict_hosts, actions = parse_rakefile.read_rake(argv[1])
    #dict_hosts, actions = parse_rakefile.read_rake("/home/thanh/GitHub/CITS3002-Project/rake-p/hardtest")

    for sets in actions:
        handle_conn(sets, dict_hosts)
        
if __name__ == "__main__":
    main(sys.argv)