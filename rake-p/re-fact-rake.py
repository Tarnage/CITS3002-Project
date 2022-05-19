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
    def __init__(self, ip: str, port: int, current_ack: int):
        self.ip = ip
        self.port = port
        self.current_ack = current_ack
        self.next_file_index = 1

        self.sockfd = -1
        self.ACK = Ack()
        self.action = None


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

    
    def send_int(self, payload: int):
        ''' Helper to send the ints in big endian padded to 4 bytes
            Args:
                payload(int): int to send
        '''
        preamble = payload.to_bytes(MAX_BYTE_SIGMA, byteorder=BIG_EDIAN)
        sent_bytes = self.sockfd.send(preamble)


    def disconnect(self):
        self.sockfd.shutdown(socket.SHUT_RDWR)
        self.sockfd.close()
        self.sockfd = -1


    def add_actions(self, actions: Action):
        self.actions = actions


    def files_remaining(self) -> int:
        return (len(self.actions.requires)-1) - (self.next_file_index-1)


    def get_next_file(self) -> str:
        filename = self.actions.requires[self.next_file_index]
        # INCREMENT AFTER ACK OF CURRENT FILE
        # self.next_file_index += 1
        return filename


    def find_files(self, filename: str) -> str:
        ''' Searches entire computer for file
            Args:
                filename(str): file name to find
        '''
        result = None
        # start = time.time()
        # TOP-DOWN FROM THE ROOT
        for root, dir, files in os.walk("/"):
            if filename in files:
                result = (os.path.join(root, filename))
                # finish = time.time()
                # #print(finish - start)
                return result


    def send_file(self):
        filename = self.get_next_file()
        path = self.find_files(filename)

        if path != None:
            if self.is_bin_file(path):
                self.send_bin_file(filename, path)
            else:
                self.send_txt_file(filename, path)
        else:
            print(f"{filename} COULD NOT BE LOCATED!")
            sys.exit(1)


    def recv_int(self) -> int:
        ''' Helper to get the size of incoming payload also to get expected integers
            Since all integers are 8 bytes
            Args:
                sd(socket): socket descriptor of the connection

            Return:
                result(int): The size of incoming payload
        '''
        size = b''
        more_size = b''
        while len(size) < MAX_BYTE_SIGMA:
            try:
                more_size = self.sockfd.recv( MAX_BYTE_SIGMA - len(size) )
                if not more_size:
                    break
            except socket.error as err:
                if err.errno == 35:
                    time.sleep(0)
                    continue
            size += more_size

        result = int.from_bytes(size, BIG_EDIAN)
        return result


    def send_cmd(self):
        pass


    def process(self, read: bool) -> bool:
        finished = False

        if read:
            preamble = self.recv_int()
            
            if preamble == self.ACK.CMD_ACK:
                # SEND THE NEXT FILE
                self.next_file_index += 1
                pass

            elif preamble == self.ACK.CMD_RETURN_STATUS:
                r_code = self.recv_int()
                preamble = self.recv_int()

                if preamble == self.ACK.CMD_RETURN_FILE:
                    self.recv_file()
                else:
                    print("SOMETHING WENT WRONG RECVEING THE FILE")
                
                finished = True


            elif preamble == self.ACK.CMD_RETURN_STDERR:
                finished = True

            elif preamble == self.ACK.CMD_RETURN_STDOUT:
                finished = True

            elif preamble == self.ACK.CMD_NO_OUTPUT:
                print("WORKED")
                r_code = self.recv_int()
                finished = True
        
        else:
            if self.current_ack == self.ACK.CMD_SEND_FILE:
                if self.files_remaining() > 0:
                    self.send_file()
                else:
                    self.send_cmd()
                    self.current_ack = self.ACK.CMD_RETURN_STATUS
                



        return finished
            


        

#-------------------------------------------------------------------
# ENUM CLASS
ACK = Ack()




def create_quote_team(hosts: dict) -> dict:
    '''returns a dictionary of fileno -> Connection Object'''

    slaves = dict()

    for ip in hosts:
        port = hosts[ip]
        cost = MAX_INT
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
        slaves[fileno] = (ip, hosts, cost)

    return slaves


def create_local_host() -> Connection:
    '''Helper to create the local host connection'''
    default_port = parse_rakefile.get_default_port()
    return Connection(LOCAL_HOST, default_port, current_ack=-1)


def get_lowest_quote(queue: dict) -> tuple:

    lowest = MAX_INT
    l_ip = ""
    l_port = -1

    for key in queue:
        ip, port, cost = queue[key]
        if cost < lowest:
            l_ip = ip
            l_port = port

    return (l_ip, l_port)

def recv_int(sd: socket) -> int:
    ''' Helper to get the int of incoming payload
        Args:
            sd(socket): socket descriptor of the connection

        Return:
            result(int): The int of incoming payload
    '''
    size = b''
    more_size = b''
    while len(size) < MAX_BYTE_SIGMA:
        try:
            print(f"LISTENING ON {sd.getpeername()}...")
            more_size = sd.recv( (MAX_BYTE_SIGMA - len(size)) )
            if not more_size:
                break
        except socket.error as err:
            if err.errno == 35:
                #print("NO AVAILIABLE TRYING AGAIN...")
                time.sleep(0)
                continue
        size += more_size

    result = int.from_bytes(size, BIG_EDIAN)
    #print(f"RECEIVED INT {result}")
    return result

def recv_cost(sd: socket) -> int:
    preamble = recv_int(sd)
    if preamble == ACK.CMD_QUOTE_REPLY:
        cost = recv_int(sd)
        return cost
    else:
        print("SOMETHING WENT WRONG RECEIVING THE COST")


def send_int(sd: socket, payload: int):
    ''' Helper to send the ints in big endian padded to 4 bytes
        Args:
            payload(int): int to send
    '''
    preamble = payload.to_bytes(MAX_BYTE_SIGMA, byteorder=BIG_EDIAN)
    sent_bytes = sd.send(preamble)



def send_cost_req(sockfd: socket):
    send_int(sockfd, ACK.CMD_QUOTE_REQUEST)



def handle_conn(sets: list, hosts: dict):

    input_sockets = list()
    output_sockets = list()

    # conn_dict KEY=fileno, VALUE=Connection Object
    conn_dict = dict()

    local_host = create_local_host()

    actions_exe = 0
    next_action = 0
    remaing_actions = len(sets)

    quote_queue = dict()
    quote_recv = 0
    curr_qoute_req = 0
    print("REMAINING ACTIONS ",remaing_actions)
    while actions_exe < remaing_actions:
        try:

            # IF WE STILL HAVE ACTIONS TO EXE OR GET COST FOR
            if next_action < remaing_actions:
                print("CHECKING",sets[next_action].remote)
                # IF ITS A LOCAL CMD USE LOCAL HOST OBJ
                if not sets[next_action].remote:
                    local_host.add_actions(sets[next_action])
                    fileno = local_host.connect()
                    conn_dict[fileno] = local_host
                    local_host.current_ack = local_host.ACK.CMD_SEND_FILE
                    output_sockets.append(fileno)
                    next_action += 1

                # SEND OUT COST REQUESTS FOR THE NEXT ACTION
                if (next_action < remaing_actions) and (sets[next_action].remote) and (quote_recv == 0):
                    quote_queue = create_quote_team(hosts)

                    for sd in quote_queue:
                        output_sockets.extend(sd)
            
                # IF WE HAVE RECV A QUOTE FROM ALL AVAILIABLE HOSTS
                elif (next_action < remaing_actions) and (quote_recv == len(hosts)):
                    quote_recv = 0
                    ip, port = get_lowest_quote(quote_queue)
                    quote_queue = dict()
                    new_client = Connection(ip, port, ACK.CMD_SEND_FILE)
                    new_client.add_actions(sets[next_action])
                    fileno = new_client.connect()
                    conn_dict[fileno] = new_client
                    output_sockets.append(fileno)
                    next_action += 1
                
            read_sockets, write_sockets, error_sockets = select.select(input_sockets, output_sockets, [], TIMEOUT)

            for sockfd in read_sockets:
                if sockfd:
                    if sockfd in input_sockets:
                        input_sockets.remove(sockfd)
                    
                    if sockfd in conn_dict:
                        conn = conn_dict[sockfd]

                        finished = conn.process(read=True)

                        if not finished:
                            output_sockets.append(sockfd)
                        else:
                            actions_exe += 1
                            conn.disconnect()
                            del conn_dict[sockfd]

                    # ITS A COST REQ
                    else:
                        cost = recv_cost(sockfd)
                        ip, port, curr_cost = quote_queue[sockfd]
                        curr_cost = cost
                        quote_queue[sockfd] = (ip, port, curr_cost)
                        quote_recv += 1

            for sockfd in write_sockets:
                if sockfd:
                    if sockfd in output_sockets:
                        output_sockets.remove(sockfd)
                    
                    if sockfd in conn_dict:
                        conn = conn_dict[sockfd]

                        finished = conn.process(read=False)

                        if not finished:
                            input_sockets.append(sockfd)
                        else:
                            conn.disconnect()
                            del conn_dict[sockfd]

                    # ITS A COST REQ
                    else:
                        send_cost_req(sockfd)
                        input_sockets.append(sockfd)

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