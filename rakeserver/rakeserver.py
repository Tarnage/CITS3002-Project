#!/usr/bin/env python3

import getopt
import shutil
import time
import random
import os
import socket
import sys
import subprocess
import signal
import psutil

# DEFAULT PORSTS AND HOSTS
SERVER_PORT = 50008
SERVER_HOST = '127.0.0.1'
# THE STANDARD THIS PROGRAM WILL USE TO ENCODE AND DECODE STRINGS
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
# INTS OR ACKS ARE 8 BYTES LONG
MAX_BYTE_SIGMA = 4
# USE BIG BIG_EDIAN FOR BYTE ORDER
BIG_EDIAN = 'big'

# IF SERVER IS LOCAL HOST
is_local_host = False

# OPTSARGS
sleep = False
rand = random.randint(1, 3)
sleep_timer = os.getpid() % rand + 2
#print( f'sleep for: {timer}' )
remove_temp = False

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


class FileStats():
	''' Class to help track files on the server created by the client
	'''
	def __init__(self, filename, size, path):
		self.filename = filename
		self.size = size
		self.path = path


class Client():
    ''' This object represents the connection from client to server
        A new Client instance is created everytime the program forks a process
    '''
    def __init__(self, sockfd: socket, addr: tuple, current_ack: int):
        self.sockfd = sockfd
        self.addr = addr
        self.current_ack = current_ack
        self.ACK = Ack()
        self.finished = False
        self.return_file = None
        self.path_return_file = None
        self.r_output = None
        self.stderr = None
        self.stdout = None

    def recv_int(self) -> int:
        ''' Helper to get the int of incoming payload
            Return:
                result(int): The int of incoming payload
        '''
        size = b''
        more_size = b''
        while len(size) < MAX_BYTE_SIGMA:
            try:
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
        ''' Helper to make sure temp directory exists if not create one
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

    def recv_string(self) -> str:
        ''' Helper to receive strings from the connection
            Return:
                (str): received from the connection   
        '''
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

    def recv_txt_file(self) -> None:
        ''' Writes strings to a file. This is used to transfer source code from Client to Server
        '''
        peer_dir = f'{self.addr[0]}.{self.addr[1]}'
        self.check_temp_dir(peer_dir)
        tmp = f"./tmp/{peer_dir}/"

        filename = self.recv_string()
        size = self.recv_int()

        buffer = ""
        while len(buffer) < size:
            print(f"{len(buffer)}/{size}", end="\r")
            buffer = self.sockfd.recv(size).decode(FORMAT)
        if sleep:
            time.sleep(sleep_timer)
        print(f"{len(buffer)}/{size}")

        try:
            time.sleep(0)
            with open(tmp + filename, "w") as f:
                f.write(buffer)

        except OSError as err:
            sys.exit(f'File creation failed with error: {err}')

    def recv_bin_file(self) -> None:
        ''' Writes strings to a file. This is used to transfer source code from Client to Server
        '''
        peer_dir = f'{self.addr[0]}.{self.addr[1]}'
        self.check_temp_dir(peer_dir)
        tmp = f"./tmp/{peer_dir}/"

        filename = self.recv_string()
        size = self.recv_int()

        buffer = b""
        while len(buffer) < size:
            print(f"{len(buffer)}/{size}", end="\r")
            buffer = self.sockfd.recv(size)
        if sleep:
            time.sleep(sleep_timer)
        print(f"{len(buffer)}/{size}")

        try:
            time.sleep(0)
            with open(tmp + filename, "wb") as f:
                f.write(buffer)

        except OSError as err:
            sys.exit(f'File creation failed with error: {err}')

    def recv_next_action(self) -> None:
        ''' Helper to read next action
        '''
        preamble = self.recv_int()
        self.current_ack = preamble

    def send_int(self, preamble: int) -> int:
        ''' Helper to send the ints in big endian padded to 4 bytes
            Args:
                payload(int): int to send
            Return:
                sent_bytes(int): The number of bytes sent
        '''
        payload = preamble.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
        sent_bytes = self.sockfd.send(payload)
        return sent_bytes

    def scan_dir(self, path: str):
        ''' Helper for run_cmd() This function will assign a FileStats object
            to current objects return_file property
            Args:
                path(str): The directory path of the target
        '''
        filename = ""
        ctime = 0
        file_size = 0
        with os.scandir(path) as dir_entries:
            for entry in dir_entries:
                info = entry.stat()
                if info.st_ctime_ns > ctime:
                    filename = entry.name
                    ctime = info.st_ctime_ns
                    file_size = info.st_size
                    path = entry.path
                    
        self.return_file = FileStats(filename, file_size, path)

    def run_cmd(self, cmd: str) -> None:
        ''' Runs the cmd sent by the client
            This function will assign path_return_file property to a string pointing to 
            the directory of the output file, if any.
            r_output will be assign to the compeleted process containing the return codes, stderr, stdout if any.
            Args:
                cmd(str): to be executed in the shell
        '''
        peer_dir = f'{self.addr[0]}.{self.addr[1]}'
        self.check_temp_dir(peer_dir)
        path = str('./tmp/' + peer_dir)
        print(f'RUNNING COMMAND: {cmd}')

        p = subprocess.Popen(cmd, shell=True, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setpgrp)
        p.wait()
        self.stdout, self.stderr =  p.communicate()
        self.r_output = p.returncode
        print(f"CODE: {p.returncode}")
        self.scan_dir(path)
        self.path_return_file = path
        

    def send_string(self, string: str):
        ''' Helper that formats a string and sends it to the connection
            Args:
                string(str): payload
        '''
        payload = string.encode(FORMAT)
        self.send_int(len(payload))
        self.sockfd.send(payload)

    def send_return_file(self):
        ''' Returns the output file.
            Information on the return file is found
            in the return_file property
        '''
        path = self.path_return_file + '/' + self.return_file.filename
        payload = b''
        with open(path, 'rb') as f:
            payload = f.read()

        self.send_string(self.return_file.filename)
        self.send_int(len(payload))
        self.sockfd.send( payload )
        print(f"RETURNED: {self.return_file.filename}")

    def send_std(self, payload: bytes):
        ''' This function will decode and encode to ensure correct formatting
            before it is formatted into utf-8 and sent
            Args:
                payload(bytes): The std messgae to send
        '''
        # MAKE SURE ITS IN THE RIGHT ENCDOING
        decode = payload.decode(FORMAT)
        encode = decode.encode(FORMAT)

        # SEND THE SIZE OF THE NAME FIRST
        self.send_int(len(encode))

        # SEND THE ACTUAL PAYLOAD
        self.sockfd.send( encode )

    def rm_client_files(self):
        '''Helper called at the end of the connection to remove temp files and folders'''
        peer_dir = f'{self.addr[0]}.{self.addr[1]}'
        tmp = f"./tmp/{peer_dir}/"

        if os.path.isdir(tmp):
            try:
                shutil.rmtree(tmp, ignore_errors=False)
            except OSError as err:
                sys.exit("Error occured while deleting temp directory: {err}")

    def disconnect(self):
        ''' Shutdown connection
        '''
        self.sockfd.shutdown(socket.SHUT_RDWR)
        self.sockfd.close()
        self.sockfd = -1

    def proc_req(self):
        ''' Main processing loop
            Only exits once a return code and/or file is sent, this represents the
            compeletion of the connection
        '''
        try:
            while self.sockfd:
                
               	if sleep:
                    time.sleep(sleep_timer)

                if(self.current_ack == self.ACK.CMD_SEND_FILE):
                    self.recv_txt_file()
                    self.send_int(self.ACK.CMD_ACK)

                elif(self.current_ack == self.ACK.CMD_BIN_FILE):
                    self.recv_bin_file()
                    self.send_int(self.ACK.CMD_ACK)

                elif(self.current_ack == self.ACK.CMD_EXECUTE):
                    payload = self.recv_string()
                    self.run_cmd(payload)
                    r_code = self.r_output

                    # IF NO OUTPUT FILE WAS PRODUCED AND WAS A SUCCESSFULLY RUN
                    if (self.return_file.filename == "") and (r_code == 0):
                        self.send_int(self.ACK.CMD_NO_OUTPUT)
                        self.send_int(r_code)

                    # EXECUTION WAS SUCCESSFUL, NOW WE GET READY TO SEND THE OUTPUT FILE
                    elif r_code == 0:
                        self.send_int(self.ACK.CMD_RETURN_STATUS)
                        self.send_int(r_code)
                        self.send_int( self.ACK.CMD_RETURN_FILE)
                        self.send_return_file()

                    # EXECUTION FAILED WITH WARNING
                    elif 0 < r_code < 5:
                        self.send_int(self.ACK.CMD_RETURN_STDERR)
                        self.send_int(r_code)
                        self.send_std(self.stderr)

                    # EXECUTION HAD A FATAL ERROR
                    else:
                        self.send_int(self.ACK.CMD_RETURN_STDOUT)
                        self.send_int(r_code)
                        self.send_std(self.stdout)
                    
                    self.disconnect()
                    self.finished = True

                if not self.finished:
                    self.recv_next_action()
        except Exception as err:
            print(f"ERROR: Connection to {self.addr} disconnected!")

        
class Server():
    ''' Server Class
        Contains some methods to handle the server
    '''
    def __init__(self, ip: str, port: int, backlog=1):
        self.ip = ip
        self.port = port
        self.sockfd = -1
        self.backlog = backlog
        self.ACK = Ack()
        self.children = list()

    def create_server(self) -> int:
        ''' Binds the object to an ip and port
            Note: it does not start listening until the listen() method is called.
            Return:
                int: 1 on success 0 on failure
        '''
        try:
            self.sockfd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sockfd.bind( (self.ip, self.port) )
            print(f"SERVER: {self.ip}:{self.port}")
        except socket.error as err:
            if err.errno == 98:
                print(f'Binding failed with error: {err}')
                
            else:
                print(f'Socket creation failed with error {err}')
            return 0

        return 1

    def listen(self) -> None:
        ''' Set the server to listen for incoming connections
        '''
        self.sockfd.listen()

    def accept(self) -> tuple:
        ''' Accepts clients requesting connection
            Return:
                tuple: (socket object, address info)
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
        payload = preamble.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
        size_sent = client.send(payload)
        if size_sent == MAX_BYTE_SIGMA:
            return 1
        else:
            return 0

    def calculate_cost(self) -> int:
        ''' Randomly return a number between 1-100'''
        # seed for testing
        random.seed(time.time() % 8)
        return random.randint(1, 100)

    def send_cost(self, client: socket):
        ''' Sends a random number between 1-10 to a socket

            Args:
                sd(socket): Which socket to send the quote.
        '''
        try:
            self.send_int(client, self.ACK.CMD_QUOTE_REPLY)
            cost = self.calculate_cost()
            
            self.send_int(client, cost)
            print(f'<---- SENDING QUOTE: {cost}')
        except socket.error as err:
            print(f"Error {err}\nConnection to {client.getpeername()} disconnected!")

    def sig_handler(self, signum, frame):
        try:
            # EXECPTION RAISED WHEN SUBPROCESS FROM run_cmd IS SINGALED
            # WE ONLY WANT DIRECT CHILDREN OF THE PARENT PROCESS
            child_pid, _ = os.waitpid(-1, os.WNOHANG)
            parent = psutil.Process(os.getpid())
            if parent.pid == os.getpid():
                os.wait()
        except Exception as err:
            pass
#------------------------------------------------MAIN------------------------------------------------------------
# INIT ENUM CLASS
ACK = Ack()

def usage(prog):
	print(f"Usage: {prog} [OPTIONS]...PORT...")
	print("Description")
	print("\tThe purpose of this server program is to receive source files and compile them on the local machine")
	print("\tYou are able to combine opts such as -wi [IP]...[PORT] to create a socket connecting to IP:PORT and the program will wait between send requests")
	print("\tThe [i] opts must always be last followed by the [IP]...[PORT]")
	print("Option")
	print("\tIf no options are used, a port number must be given as an argument\n")
	print("\t-h\tdisplay this help and exit\n")
	print("\t-d\twill run on localhost and port: 50008\n")
	print("\t-v\tverbose mode - default is ON\n")
	print("\t-w\twill add a randomised wait timer (1-3secs) between each send request\n")
	print("\t-i\trequires ip and port as arguments. i.e. ./rakeserver -i 127.0.0.1 80006\n")
	print("\t-r\twill NOT remove temporary files and folders created during the connection of a client\n")


def handle_conn(server: Server) -> None:
    ''' Main function to deal with client connections
        Args:
            server(Server): Instance of a Server class
    '''
    if server.create_server():
        server.listen()
        try:
            while True:
                conn, addr = server.accept()
                preamble = server.recv_int(conn)
                if sleep:
                    time.sleep(sleep_timer)

                if preamble == ACK.CMD_QUOTE_REQUEST:
                    server.send_cost(conn)
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                else:
                    print("FORKED..")
                    child = os.fork()
                    print(f"CHILD {os.getpid()}")
                    if child == 0:
                        client = Client(conn, addr, preamble)
                        client.proc_req()
                        if remove_temp:
                            client.rm_client_files()
                        print(f"{client.addr}DISCONNECTING..")
                        sys.exit(0)
                    elif child > 0:
                        signal.signal(signal.SIGCHLD, server.sig_handler)
                    else:
                        sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
        except socket.error as err:
            print(f"Error {err}\nConnection to {addr} disconnected!")


def main(ip=SERVER_HOST, port=SERVER_PORT):
    server = Server(ip, port, DEFAULT_BACKLOG)

    handle_conn(server)


if __name__ == "__main__":
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
					sys.stdout = open(os.devnull, 'w')
				elif o == "-d":
					main()
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
			print(err)
			usage(prog)
