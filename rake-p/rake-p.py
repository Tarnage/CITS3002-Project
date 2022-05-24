#!/usr/bin/env python3

import parse_rakefile
from parse_rakefile import Action
import sys
import socket
import select
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
MAX_INT 		= sys.maxsize

#------------------------------------------------CLASSES------------------------------------------------------------

class Ack:
    ''' ENUM  Class'''
    def __init__(self):
        self.CMD_DEBUG = 0

        self.CMD_QUOTE_REQUEST = 1
        self.CMD_QUOTE_REPLY = 2

        self.CMD_BIN_FILE = 3
        self.CMD_SEND_FILE = 4

        self.CMD_EXECUTE = 5
        self.CMD_RETURN_STATUS  = 6
        self.CMD_RETURN_STDOUT  = 7
        self.CMD_RETURN_STDERR  = 8
        self.CMD_RETURN_FILE = 9

        self.CMD_ACK = 10
        self.CMD_NO_OUTPUT = 11


class Connection:
    ''' Object that represents each connection
        This object is used to track files to send or receive.
    '''
    def __init__(self, ip: str, port: int, current_ack: int):
        self.ip = ip
        self.port = port
        self.current_ack = current_ack
        self.next_file_index = 1

        self.sockfd = -1
        self.ACK = Ack()
        self.action = None

    def connect(self):
        '''requests connection to the server and returns the fileno of the socket'''
        try:
            self.sockfd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.sockfd.connect( (self.ip, self.port) )
        except socket.error as err:
            if err.errno == 111:
                sys.exit( ( f'Connection refused with error: {err}' ) )
            else: 
                sys.exit( f'socket creation failed with error: {err}' )

    def send_int(self, payload: int) -> int:
        ''' Helper to send the ints in big endian padded to 4 bytes
            Args:
                payload(int): int to send
            Return:
                sent_bytes(int): The number of bytes sent
        '''
        preamble = payload.to_bytes(MAX_BYTE_SIGMA, byteorder=BIG_EDIAN)
        sent_bytes = self.sockfd.send(preamble)
        return sent_bytes

    def disconnect(self):
        ''' Shutdown connection
        '''
        self.sockfd.shutdown(socket.SHUT_RDWR)
        self.sockfd.close()
        self.sockfd = -1

    def add_actions(self, actions: Action):
        ''' Assigns the action property to an Action object
        '''
        self.actions = actions

    def files_remaining(self) -> int:
        ''' Returns the number of files left to send
        '''
        return (len(self.actions.requires)-1) - (self.next_file_index-1)

    def get_next_file(self) -> str:
        ''' Extracts the filename from the path
            Return:
                tuple: (filename, path)
        '''
        path = self.actions.requires[self.next_file_index]
        filename = path.split("/")[-1]
        return filename, path

    def recv_string(self):
        size = self.recv_int()
        string = b''
        more_size = b''
        while len(string) < size:
            try:
                more_size = self.sockfd.recv( size - len(string) )
                if not more_size:
                    break
            except socket.error as err:
                if err.errno == 35:
                    time.sleep(0)
                    continue

            string += more_size
        
        return string.decode(FORMAT)

    def send_string(self, string: str):
        ''' Helper that formats a string and sends it to the connection
            Args:
                string(str): payload
        '''
        payload = string.encode(FORMAT)
        self.send_int(len(payload))
        self.sockfd.send(payload)

    def is_bin_file(self, path: str) -> bool:
        ''' Helper to ensure we send the file in the right format
            Args:
                filename(str): location to the file.
        '''
        try:
            with open(path, 'tr') as check_file:  # try open file in text mode
                check_file.read()
                return False
        except:  # if fail then file is non-text (binary)
            return True

    def send_bin_file(self, filename: str, path: str):
        ''' Transfer binary file
        
            Args:
                filename(str): file name
                path(str): path to file
        '''
        payload = b''
        with open(path, 'rb') as f:
            payload = f.read()
        self.send_int(self.ACK.CMD_BIN_FILE)
        self.send_string(filename)
        self.send_int(len(payload))
        self.sockfd.send( payload )


    def send_txt_file(self, filename: str, path: str):
        ''' Send file contents to server

            Args:
                filename(str): Name of file to transfer
                path(str): path to file
        '''
        contents = ""
        with open(path, "r") as f:
            contents = f.read()

        payload = contents.encode(FORMAT)
        self.send_int(self.ACK.CMD_SEND_FILE)
        self.send_string(filename)
        self.send_int(len(payload))
        self.sockfd.send( payload )

    def send_file(self):
        filename, path = self.get_next_file()
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
        payload = self.actions.cmd
        self.send_int(self.ACK.CMD_EXECUTE)
        self.send_string(payload)

    def recv_file(self):
        ''' Receive binary file from server connection
        '''

        filename = self.recv_string()
        size = self.recv_int()
        try:
            with open(filename, "wb") as f:
                buffer = b""
                while len(buffer) < size:
                    buffer += self.sockfd.recv(size - len(buffer))

                f.write(buffer)

        except OSError as err:
            sys.exit(f'File creation failed with error: {err}')

    def read(self) -> bool:
        finished = False
        preamble = self.recv_int()
        
        # CONNECTION OBJECTS ONLY EXPECT AN ACK FOR THE NEXT ACTION
        # OR A RETURN STATUS
        if preamble == self.ACK.CMD_ACK:
            # INCREMENT INDEX FOR THE NEXT FILE
            self.next_file_index += 1
        else:
            r_code = self.recv_int()

            if preamble == self.ACK.CMD_RETURN_STATUS:
                preamble = self.recv_int()

                if preamble == self.ACK.CMD_RETURN_FILE:
                    self.recv_file()
                    print("RECV FILE")
                else:
                    print("SOMETHING WENT WRONG RECVEING THE FILE")
                    sys.exit(1)

            elif preamble == self.ACK.CMD_RETURN_STDERR:
                err_msg = self.recv_string()
                print(f"ERROR FROM {self.sockfd.getpeername()}:")
                print(f"RETURN CODE: {r_code}")
                sys.stderr.write(err_msg)
                sys.exit(r_code)

            elif preamble == self.ACK.CMD_RETURN_STDOUT:
                err_msg = self.recv_string()
                print(f"ERROR FROM {self.sockfd.getpeername()}:")
                print(f"RETURN CODE: {r_code}")
                sys.stdout.write(err_msg)
                sys.exit(r_code)

            elif preamble == self.ACK.CMD_NO_OUTPUT:
                pass

            finished = True

        return finished

    def write(self) -> bool:
        if self.current_ack == self.ACK.CMD_SEND_FILE:
            if self.files_remaining() > 0:
                self.send_file()
            else:
                self.send_cmd()
                self.current_ack = self.ACK.CMD_RETURN_STATUS
        
        # NEVER FINISED UNTIL WE GET A RETURN FILE OR MESSAGE FROM SERVER
        return False

#------------------------------------------------MAIN------------------------------------------------------------
# INIT ENUM CLASS
ACK = Ack()

def create_quote_team(hosts: dict) -> dict:
    ''' Creates the connections to all available hosts
        Args:
            hosts(dict): key=ip(str), value=ports(int)
        Return:
            slaves(dict): key=socket, value=tuple(ip(str), port(int), cost(int)) 
    '''

    slaves = dict()

    for ip in hosts:

        port = hosts[ip]
        cost = MAX_INT
        try:
            sd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            sd.connect( (ip, port) )
            
        except socket.error as err:
            if err.errno == 111:
                sys.exit( ( f'Connection refused with error: {err}' ) )
            else: 
                sys.exit( f'socket creation failed with error: {err}' )

        fileno = sd.fileno()
        slaves[sd] = (ip, hosts[ip], cost)

    return slaves


def create_local_host() -> Connection:
    ''' Helper to create the local host connection
        Return:
            Connection(obj): connection representing local host
    '''
    default_port = parse_rakefile.get_default_port()
    return Connection(LOCAL_HOST, default_port, current_ack=-1)


def get_lowest_quote(slaves: dict) -> tuple:
    ''' Helper to calculate lowest cost
        Args:
            slaves(dict): key=socket, value=tuple(ip(str), port(int), cost(int))
        Return:
            Tuple(str, int): The connection with the lowest quote
    '''

    lowest = MAX_INT
    l_ip = ""
    l_port = -1

    for key in slaves:
        ip, port, cost = slaves[key]
        if cost < lowest:
            lowest = cost
            l_ip = ip
            l_port = port

    return (l_ip, l_port)


def recv_int(sd: socket) -> int:
    ''' Helper to get the int of incoming payload
        Args:
            sd(socket): socket descriptor of the connection
        Return:
            result(int): The int of received
    '''
    size = b''
    more_size = b''
    while len(size) < MAX_BYTE_SIGMA:
        try:
            more_size = sd.recv( (MAX_BYTE_SIGMA - len(size)) )
            if not more_size:
                break
        except socket.error as err:
            if err.errno == 35:
                time.sleep(0)
                continue
        size += more_size

    result = int.from_bytes(size, BIG_EDIAN)
    return result


def recv_cost(sd: socket) -> int:
    ''' Helper to receive cost - Will return MAX_INT if preamble is not what is expected.
        Args:
            sd(socket): socket descriptor of the connection
        Return:
            result(int): The cost of received
    '''
    preamble = recv_int(sd)
    if preamble == ACK.CMD_QUOTE_REPLY:
        cost = recv_int(sd)
        return cost
    else:
        print("SOMETHING WENT WRONG RECEIVING THE COST")
        return MAX_INT


def send_int(sd: socket, payload: int) -> None:
    ''' Helper to send integers, such as ENUMS and costs
        Args:
            sd(socket): the connection to send
            payload(int): int to send
    '''
    preamble = payload.to_bytes(MAX_BYTE_SIGMA, byteorder=BIG_EDIAN)
    sent_bytes = sd.send(preamble)


def send_cost_req(sd: socket) -> None:
    ''' Helper to send quote request
        Args:
            sd(socket): the connection to send
    '''
    send_int(sd, ACK.CMD_QUOTE_REQUEST)

def handle_conn(sets: list, hosts: dict):
    ''' Handles the main logic of the program
        Args:
            sets(list): the Rakefile after the parse.
            hosts(dict): key=ip value=ports
    '''

    input_sockets = list()
    output_sockets = list()

    # conn_dict KEY=fileno, VALUE=Connection Object
    conn_dict = dict()

    # LOCAL HOST CONNECTION
    local_host = create_local_host()

    actions_exe = 0
    next_action = 0
    remaing_actions = len(sets)

    quote_queue = dict()
    quote_recv = 0
    curr_qoute_req = 0

    while actions_exe < remaing_actions:
        try:

            # IF WE STILL HAVE ACTIONS TO EXE OR GET COST FOR
            if next_action < remaing_actions:
                # IF ITS A LOCAL CMD USE LOCAL HOST OBJ
                if not sets[next_action].remote:
                    local_host.add_actions(sets[next_action])

                    local_host.connect()
                    conn_dict[local_host.sockfd] = local_host
                    local_host.current_ack = local_host.ACK.CMD_SEND_FILE
                    output_sockets.append(local_host.sockfd)
                    next_action += 1
                    curr_qoute_req += 1

                # SEND OUT COST REQUESTS FOR THE NEXT ACTION
                if (curr_qoute_req == next_action) and (sets[next_action].remote) and (quote_recv == 0):
                    print(f"GETTING QUOTE FOR: {curr_qoute_req}")
                    quote_queue = create_quote_team(hosts)

                    for sd in quote_queue:
                        output_sockets.append(sd)
                    curr_qoute_req += 1
            
                # IF WE HAVE RECVEIVED ALL QUOTES FOR THE NEXT ACTION
                elif (next_action < remaing_actions) and (quote_recv == len(hosts)):
                    print(f"ACTION no-{next_action} SENT TO PROCESS")
                    quote_recv = 0
                    ip, port = get_lowest_quote(quote_queue)
                    quote_queue = dict()
                    new_client = Connection(ip, port, ACK.CMD_SEND_FILE)
                    new_client.add_actions(sets[next_action])
                    new_client.connect()
                    conn_dict[new_client.sockfd] = new_client
                    output_sockets.append(new_client.sockfd)
                    next_action += 1
                
            read_sockets, write_sockets, _ = select.select(input_sockets, output_sockets, [], TIMEOUT)

            for sockfd in read_sockets:
                if sockfd:
                    if sockfd in input_sockets:
                        input_sockets.remove(sockfd)
                    
                    # ITS EXPECTING AN ACK
                    if sockfd in conn_dict:
                        conn = conn_dict[sockfd]

                        finished = conn.read()

                        if not finished:
                            output_sockets.append(sockfd)
                        else:
                            actions_exe += 1
                            conn.disconnect()
                            del conn_dict[sockfd]

                    # ITS A COST REQ
                    else:
                        cost = recv_cost(sockfd)
                        (ip, port, curr_cost) = quote_queue[sockfd]
                        curr_cost = cost
                        quote_queue[sockfd] = (ip, port, curr_cost)
                        quote_recv += 1

            for sockfd in write_sockets:
                if sockfd:
                    if sockfd in output_sockets:
                        output_sockets.remove(sockfd)
                    
                    # ITS SENDING AN ACTION
                    if sockfd in conn_dict:
                        conn = conn_dict[sockfd]

                        finished = conn.write()

                        # CLIENT ALWAYS EXPECTS A RESPONSE AFTER A WRITE
                        input_sockets.append(sockfd)

                    # ITS A COST REQ
                    else:
                        send_cost_req(sockfd)
                        input_sockets.append(sockfd)

        except KeyboardInterrupt:
            for sock in conn_dict:
                conn_dict[sock].disconnect()
            sys.exit(1)

def main(argv):
    dict_hosts, actions = parse_rakefile.read_rake(argv[1])

    for sets in actions:
        handle_conn(sets, dict_hosts)
        
if __name__ == "__main__":
    main(sys.argv)