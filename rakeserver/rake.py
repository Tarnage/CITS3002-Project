#!/usr/bin/env python3

import getopt
import shutil
import time
import random
import os
import socket
import sys
import subprocess

# DEFAULT PORSTS AND HOSTS
SERVER_PORT = 50008
#SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_HOST = '127.0.0.1'
# THE STANDARD THIS PROGRAM WILL USE TO ENCODE AND DECODE STRINGS
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
# INTS OR ACKS ARE 8 BYTES LONG
MAX_BYTE_SIGMA = 4
# USE BIG BIG_EDIAN FOR BYTE ORDER
BIG_EDIAN = 'big'


#------------------------------------------------CLASSES------------------------------------------------------------

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


class FileStats():
	''' Class to help track files on the server created by the client
	
	'''
	def __init__(self, filename, size, path):
		self.filename = filename
		self.size = size
		self.path = path


class Client():
    ''' This object represents the connection from client to server
    '''
    def __init__(self, sockfd: socket, addr: tuple, current_ack: int):
        self.sockfd = sockfd
        self.addr = addr
        self.current_ack = current_ack
        self.ACK = Ack()
        self.finished = False

    def recv_int(self) -> int:
        ''' Helper to get the int of incoming payload
            Args:
            Return:
                result(int): The int of incoming payload
        '''
        size = b''
        more_size = b''
        while len(size) < MAX_BYTE_SIGMA:
            try:
                print(f"LISTENING ON {self.sockfd.getpeername()}...")
                more_size = self.sockfd.recv( (MAX_BYTE_SIGMA - len(size)) )
                if not more_size:
                    break
            except socket.error as err:
                if err.errno == 35:
                    time.sleep(0)
                    continue
            size += more_size

        result = int.from_bytes(size, BIG_EDIAN)
        return result

    def check_temp_dir(self, peer_dir: str):
        ''' Helper to make sure temp dir exists if not create one

            Args;
                peer_dir(str): name of the directory to check
        '''
        if not os.path.isdir("./tmp"):
            try:
                os.mkdir("./tmp")
            except OSError as err:
                sys.exit("Directory creation failed with error: {err}")

        if not os.path.isdir(f"./tmp/{peer_dir}"):
            try:
                os.mkdir(f"./tmp/{peer_dir}")
            except OSError as err:
                sys.exit("Directory creation failed with error: {err}")

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

    def recv_txt_file(self):
        ''' Writes strings to a file. This is used to transfer source code from Client to Server

        '''
        peer_dir = f'{self.addr[0]}.{self.addr[1]}'
        self.check_temp_dir(peer_dir)
        tmp = f"./tmp/{peer_dir}/"

        filename = self.recv_string()
        #print(f"RECEIVED FILE NAME: {filename}")
        size = self.recv_int()

        buffer = ""
        while len(buffer) < size:
            #print("reading..")
            #print(f"{len(buffer)}/{size}")
            buffer = self.sockfd.recv(size).decode(FORMAT)

        #print(f"{len(buffer)}/{size}")

        try:
            with open(tmp + filename, "w") as f:
                f.write(buffer)

        except OSError as err:
            sys.exit(f'File creation failed with error: {err}')

        print("RECEIVED FILE")

    def recv_next_action(self):
        pass

    def send_int(self, preamble: int) -> int:
        ''' Helper to send the byte size of outgoing payload
            Args:
                sd(socket): socket descriptor of the connection
            Returns:
                int: 1 on success 0 on failure
        '''
        print(f"SENDING {preamble} to {self.sockfd.getpeername()} on {self.sockfd.getsockname()}")
        payload = preamble.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
        size_sent = self.sockfd.send(payload)
        if size_sent == MAX_BYTE_SIGMA:
            return 1
        else:
            return 0

    def proc_req(self):

        while not self.finished:
            
            if(self.current_ack == self.ACK.CMD_SEND_FILE):
                print("RECVING FILE")
                self.recv_txt_file()

            elif(self.current_ack == self.ACK.CMD_EXECUTE):
                print("EXECUTING")
                payload = self.recv_string()
                print(payload)
                # TODO: run cmd
                # TODO: return code to client

                time.sleep(2)

                self.send_int(self.ACK.CMD_NO_OUTPUT)
                self.send_int(0)
                self.finished = True

            if not self.finished:
                print("READING NEXT ACTION")
                break
                self.recv_next_action()

        
class Server():
    '''Server'''
    def __init__(self, ip: str, port: int, backlog=1):
        self.ip = ip
        self.port = port
        self.sockfd = -1
        self.backlog = backlog
        self.ACK = Ack()

    def create_server(self):
        try:
            self.sockfd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sockfd.bind( (self.ip, self.port) )
        except socket.error as err:
            if err.erro == 98:
                print(f'Binding failed with error: {err}')
                
            else:
                print(f'Socket creation failed with error {err}')
            return 0

        return 1

    def listen(self):
        ''' Set the server to listen for incoming connections
        '''
        self.sockfd.listen()

    def accept(self) -> tuple:
        ''' accept() -> (socket object, address info)
        '''
        return self.sockfd.accept()

    def recv_int(self, client: socket) -> int:
        ''' Helper to get the int of incoming payload
            Args:
                sd(client): socket descriptor of the connection

            Return:
                result(int): The int of incoming payload
        '''
        size = b''
        more_size = b''
        while len(size) < MAX_BYTE_SIGMA:
            try:
                print(f"LISTENING ON {client.getpeername()}...")
                more_size = client.recv( (MAX_BYTE_SIGMA - len(size)) )
                if not more_size:
                    break
            except socket.error as err:
                if err.errno == 35:
                    time.sleep(0)
                    continue
            size += more_size

        result = int.from_bytes(size, BIG_EDIAN)
        return result

    def send_int(self, client: socket, preamble: int) -> int:
        ''' Helper to send an int to client from this object
            Args:
                client(socket): socket descriptor of the connection
                preamble(int): int to send
            Returns:
                int: 1 on success 0 on failure
        '''
        print(f"SENDING {preamble} to {client.getpeername()} on {client.getsockname()}")
        payload = preamble.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
        size_sent = client.send(payload)
        if size_sent == MAX_BYTE_SIGMA:
            return 1
        else:
            return 0

    def calculate_cost(self) -> int:
        ''' Randomly return a number between 1-10'''
        # seed for testing
        # seed(1)
        return random.randint(1, 10)

    def send_cost(self, client: socket) -> int:
        ''' Sends a random number between 1-10 to a socket

            Args:
                sd(socket): Which socket to send the quote.
        '''
        self.send_int(client, self.ACK.CMD_QUOTE_REPLY)
        cost = self.calculate_cost()
        
        self.send_int(client, cost)
        print(f'<---- SENDING QUOTE: {cost}')



#------------------------------------------------MAIN------------------------------------------------------------


# INIT ENUM CLASS
ACK = Ack()

# IF LOCAL HOST SERVER
local_host = False

# OPTSARGS
sleep = False
remove_temp = False

def usage(prog):
	print(f"Usage: {prog} [OPTIONS]...PORT...")
	print("Description")
	print("\tThe purpose of this server program is to receive source files and compile them on the local machine")
	print("\tYou are able to combine opts such as -iw [IP]...[PORT] to create a socket connecting to IP:PORT and the program will wait between send requests")
	print("Option")
	print("\tIf no options are used, a port number must be given as an argument\n")
	print("\t-h\tdisplay this help and exit\n")
	print("\t-d\twill run default hostname and default port: 50008\n")
	print("\t-v\twill print on delivary of packets\n")
	print("\t-w\twill add a randomised wait timer (0-10secs) between each send request\n")
	print("\t-i\trequires ip and port as arguments. i.e. ./rakeserver -i 127.0.0.1 80006\n")
	print("\t-r\twill remove temporary files and folders created during the connection of a client\n")

def handle_conn(server: Server):

    if server.create_server():

        server.listen()

        try:
            while True:
                print("BACK IN PARENT")
                conn, addr = server.accept()
                
                preamble = server.recv_int(conn)

                if preamble == ACK.CMD_QUOTE_REQUEST:
                    server.send_cost(conn)
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                else:
                    child = os.fork()
                    print("PREAMBLE ", preamble)
                    if child == 0:
                        client = Client(conn, addr, preamble)
                        client.proc_req()

                    elif child > 0:
                        os.wait()
                    else:
                        sys.exit(1)

                

        except KeyboardInterrupt:
            sys.exit(1)





def main(ip=SERVER_HOST, port=SERVER_PORT):
    #print(f"ESTABLISHING CONNECTION ON {ip} {port}")
    server = Server(ip, port, DEFAULT_BACKLOG)

    handle_conn(server)


if __name__ == "__main__":
	# TODO move all this into main
	prog = sys.argv[0][1:]

	if (len(sys.argv) == 2 and sys.argv[1].isnumeric()):
		main(port=int(sys.argv[1]))
	elif (len(sys.argv) == 1):
		usage(prog)
		sys.exit()
	else:
		try:
			opts, args = getopt.getopt(sys.argv[1:], "hdvwi:")
			for o, a in opts:
				if o == "-h":
					usage(prog)
					sys.exit()
				elif o == "-v":
					#print("TODO verbose")
					pass
				elif o == "-d":
					#print("TODO default")
					pass
				elif o == "-w":
					sleep = True
				elif o == "-r":
					remove_temp = True
				elif o == "-i":
					if len(args) == 1:
						main(ip=a, port=int(args[0]))
					else:
						#print("Error 2 arguments are required")
						usage(prog)
						sys.exit()
				else:
					assert False, "unhandled option"

		except getopt.GetoptError as err:
			#print(err)
			usage(prog)