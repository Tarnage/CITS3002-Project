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


def calculate_cost():
	''' Randomly return a number between 1-10'''
	# seed for testing
	# seed(1)
	return random.randint(1, 10)


def send_quote(sd):
	''' Sends a random number between 1-10 to a socket

		Args:
			sd(socket): Which socket to send the quote.
	'''
	send_byte_int(sd, ACK.CMD_QUOTE_REPLY)
	cost = calculate_cost()
	print(f'<---- SENDING QUOTE: {cost}')
	cost = cost.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( cost )
	time.sleep(2)


def rm_client_files(sd):
	'''Helper called at the end of the connection to remove temp files and folders

		Args:
			sd(socket): Used to get the name of the directory
	'''
	raddr = sd.getpeername()
	peer_dir = f'{raddr[0]}.{raddr[1]}'
	dir = f"./tmp/{peer_dir}/"

	if os.path.isdir(f"./tmp/{peer_dir}"):
		try:
			shutil.rmtree(dir, ignore_errors=True)
		except OSError as err:
			sys.exit("Error occured while deleting temp directory: {err}")


def check_temp_dir(peer_dir):
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


def run_cmd(sd, cmd):
	''' Runs the cmd sent by the client

		Args:
			sd(socket): Used to create a directory with the peers name
			cmd(str): to be executed in the shell

		Returns (tuple): (int)return code, (FileStat Object) 
	
	'''
	raddr = sd.getpeername()
	peer_dir = str(raddr[0]) + "." + str(raddr[1])
	dir = str('./tmp/' + peer_dir)
	check_temp_dir(peer_dir)
	print(f'EXECUTE REQUEST FROM {raddr}')
	print(f'RUNNING COMMAND: {cmd}')
	p = subprocess.run(cmd, shell=True, cwd=dir, capture_output=True)
	print(f'COMMAND FINISHED...')

	file_attr = scan_dir(f'./tmp/{peer_dir}')

	return p, file_attr


def scan_dir(dir):
	''' Helper for run_cmd() This function will return a FileStats object 
		containg the details of the newley created file

		Args:
			dir(str): The directory path of the target

		Return:
			file_attr(FileStat Object): Contains file stats
	
	'''
	filename = ""
	ctime = 0
	file_size = 0
	path = ""

	with os.scandir(dir) as dir_entries:
		for entry in dir_entries:
			info = entry.stat()
			if info.st_ctime_ns > ctime:
				filename = entry.name
				ctime = info.st_ctime_ns
				file_size = info.st_size
				path = entry.path
				
	file_attr = FileStats(filename, file_size, path)
	return file_attr


def recv_text_file(sd):
	''' Writes strings to a file. This is used to transfer source code from Client to Server

		Args:
			sd(socket): Clients connection
			filename(str): Name of file being transferred
			size(int): Total size of file being sent in bytes.
	'''
	#TODO: peer dir gets reused to remove the dir maybe put in a dict 
	raddr = sd.getpeername()
	peer_dir = f'{raddr[0]}.{raddr[1]}'
	check_temp_dir(peer_dir)
	tmp = f"./tmp/{peer_dir}/"

	filename = recv_filename(sd)
	print(f"RECEIVED FILE NAME: {filename}")
	size = recv_byte_int(sd)

	buffer = ""
	while len(buffer) < size:
		print("reading")
		buffer += sd.recv(size - len(buffer)).decode(FORMAT)

	try:
		with open(tmp + filename, "w") as f:
			f.write(buffer)

	except OSError as err:
		sys.exit(f'File creation failed with error: {err}')


def recv_bin_file(sd):
	''' Receive binary file from server
		Args:
			sd(socket): Connection file is being sent from
	'''

	raddr = sd.getpeername()
	peer_dir = f'{raddr[0]}.{raddr[1]}'
	check_temp_dir(peer_dir)
	tmp = f"./tmp/{peer_dir}/"

	filename = recv_filename(sd)
	print(f"RECEIVED FILE NAME: {filename}")
	size = recv_byte_int(sd)

	buffer = b""
	while len(buffer) < size:
		print("reading")
		buffer += sd.recv(size - len(buffer))

	try:
		with open(tmp + filename, "wb") as f:
			f.write(buffer)

	except OSError as err:
		sys.exit(f'File creation failed with error: {err}')


def send_byte_int(sd, preamble):
	''' Helper to send the byte size of outgoing payload
		Args:
			sd(socket): socket descriptor of the connection
	'''
	payload = preamble.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall(payload)


def send_filename(sd, filename):
	''' Send filename to client
	
		Args:
			sd(socket): Connection to send the filename
			file_attr(FileStat Oject): Object contains the file stats
	'''
	# SEND THE SIZE OF THE NAME FIRST
	payload = filename.encode(FORMAT)
	send_byte_int(sd, len(payload))

	# SEND THE ACTUAL FILE NAME
	sd.sendall( payload )


def send_std(sd, payload):
	''' Send filename to client
	
		Args:
			sd(socket): Connection to send the filename
			file_attr(FileStat Oject): Object contains the file stats
	'''
	# SEND THE SIZE OF THE NAME FIRST
	send_byte_int(sd, len(payload))

	# SEND THE ACTUAL FILE NAME
	sd.sendall( payload )


# TODO: recv_filename and recv_cmd are the same fucntions
def recv_filename(sd):

	size = recv_byte_int(sd)
	filename = b''
	more_size = b''
	while len(filename) < size:
		try:
			more_size = sd.recv( size - len(filename) )
			if not more_size:
				break
		except socket.error as err:
			if err.errno == 35:
				time.sleep(0)
				continue

		filename += more_size
	
	return filename.decode(FORMAT)


def recv_cmd(sd, size):
	''' Helper to get the size of incoming payload
		Args:
			sd(socket): socket descriptor of the connection
			size(int): the size of bytes to expect

		Return:
			result(str): The command sent from client
	'''
	payload = b''
	more_size = b''
	while len(payload) < size:
		try:
			more_size = sd.recv( size - len(payload) )
			if not more_size:
				break
		except socket.error as err:
			if err.errno == 35:
				time.sleep(0)
				continue
		payload += more_size

	result = payload.decode(FORMAT)
	print("returned result")
	return result


def recv_byte_int(sd):
	''' Helper to get the size of incoming payload
		Args:
			sd(socket): socket descriptor of the connection

		Return:
			result(int): The size of incoming payload
	'''
	size = b''
	more_size = b''
	while len(size) < MAX_BYTE_SIGMA:
		try:
			more_size = sd.recv( MAX_BYTE_SIGMA - len(size) )
			if not more_size:
				break
		except socket.error as err:
			if err.errno == 35:
				time.sleep(0)
				continue
		size += more_size

	result = int.from_bytes(size, BIG_EDIAN)
	print(f"RECEIVED INT {result}")
	return result


def send_bin_file(sd, file_attr):
	''' Transfer binary file
	
		Args:
			sd(socket): Connection to send the file
			file_attr(FileStat Oject): Object contains the file stats
	'''
	print(f'<-------SENDING FILE')
	path = file_attr.path
	filename = file_attr.filename
	
	send_filename(sd, filename)

	payload = b''
	with open(path, 'rb') as f:
		payload = f.read()

	send_byte_int(sd, len(payload))

	sd.sendall( payload )
	print(f'FILE SENT...')


def handle_conn(host, port):
	'''Non Blocking server version, server will continuously poll the socket for a connection
		
		Args:
		host (str): the ip address the server will bind
		port (int): the port the server will bind 
	'''	

	global local_host

	if (host == "localhost") or (host == "127.0.0.1"):
		local_host = True

	try:
		# AF_INET IS THE ADDRESS FAMILY IP4
		# SOCK_STREAM MEANS TCP PROTOCOL IS USED
		sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("PORT SUCCESFULLY CREATED!")
		# BIND SOCKET TO PORT
		sd.bind( (host, port) )
		print( f'PORT {port} BINDED...' )
	except socket.error as err:
		if err.errno == 98:
			sys.exit(f'Binding failed with error: {err}')
		else:
			sys.exit(f'Socket creation failed with error {err}')


	# PUT THE SOCKET TO LISTEN MODE
	sd.listen(DEFAULT_BACKLOG)
	print( f"SERVER IS LISTENING FOR CONNECTIONS..." )
	print(f"PARENT PID: {os.getpid()}")
	try:
		while True:
			conn, addr = sd.accept()
			print("FORKING")
			if conn == -1:
				conn.close()
			else:
				fork = os.fork()

				if fork == -1:
					conn.close()
				elif fork == 0:
					handle_fork(conn)
				else:
					conn.close()
			
			print("RETURNED")

	except KeyboardInterrupt:
		print('Interrupted. Closing sockets...')
		# Make sure we close sockets gracefully
		sd.close()
		sys.exit()
	# except Exception as err:
	# 	print( f'ERROR occurred in {handle_conn.__name__} with code: {err}' )
	# 	sd.close()
	# 	sys.exit()


def retrun_status(sd):
	pass

def return_file(sd):
	pass

def handle_fork(sock):
	print(f"CHILD PID: {os.getpid()}")
	while True:
		# SOMETHING TO READ
		sigma = recv_byte_int(sock)
		print(f"----> RECIEVING ACK TYPE: {sigma}")

		# SLEEP
		if sleep == True:
			rand = random.randint(1, 10)
			timer = os.getpid() % rand + 2
			print( f'sleep for: {timer}' )
			time.sleep(timer)

		# REQUEST FOR COST QUOTE
		if sigma == ACK.CMD_QUOTE_REQUEST:
			print(f'COST QUOTE REQUESTED')
			send_quote(sock)
			print(f"CLOSING CONNECTION WITH {sock.getpeername()}")
			sock.close()
			sys.exit() # MAKE SURE CHILD PROCESS CLOSES OTHERWISE ZOMBIES
		
		# REQUEST TO RUN COMMAND
		elif sigma == ACK.CMD_EXECUTE:
			size = recv_byte_int(sock)
			payload = recv_cmd(sock, size)
			print(f'REQUEST TO EXECUTE...{payload}')
			# STORE RETURN CODE IN DICT 
			proc, file_attr = run_cmd(sock, payload)
			r_code = proc.returncode

			print(f"<-------- SENDING RETURN STATUS ({r_code})")

			# IF NO OUTPUT FILE WAS PRODUCED AND WAS A SUCCESSFULLY RUN
			if (file_attr.filename == "") and (r_code == 0):
				send_byte_int(sock, ACK.CMD_NO_OUTPUT)
				send_byte_int(sock, r_code)

			# EXECUTION WAS SUCCESSFUL, NOW WE GET READY TO SEND THE OUTPUT FILE
			elif r_code == 0:
				send_byte_int(sock, ACK.CMD_RETURN_STATUS)
				send_byte_int(sock, r_code)
				send_byte_int(sock, ACK.CMD_RETURN_FILE)
				send_bin_file(sock, file_attr)

			# EXECUTION FAILED WITH WARNING
			#TODO: hand error codes
			elif 0 < r_code < 5:
				send_byte_int(sock, ACK.CMD_RETURN_STDOUT)
				send_byte_int(sock, r_code)
				send_std(sock, proc.stderr)
				print("STDERR SENT --->")

			# EXECUTION HAD A FATAL ERROR
			else:
				send_byte_int(sock, ACK.CMD_RETURN_STDOUT)
				send_byte_int(sock, r_code)
				send_std(sock, proc.stdout)
				print("STDOUT SENT --->")

			print(f"CLOSING CONNECTION WITH {sock.getpeername()}")
			# DELETE THE TEMP FOLDER CREATED FOR THE CLIENT
			if remove_temp == True:
				rm_client_files(sock)
				# END OF CONNECTION

			sock.close()
			sys.exit() # MAKE SURE CHILD PROCESS CLOSES OTHERWISE ZOMBIES

		elif sigma == ACK.CMD_SEND_FILE:
			recv_text_file(sock)
			send_byte_int(sock, ACK.CMD_ACK)

		elif sigma == ACK.CMD_BIN_FILE:
			recv_bin_file(sock)
			send_byte_int(sock, ACK.CMD_ACK)
		

		# TODO: ERROR 
		elif sigma == ACK.CMD_ECHO:
			sock.close()
			sys.exit() # MAKE SURE CHILD PROCESS CLOSES OTHERWISE ZOMBIES


# WHEN SOCKETS ARE IN ack_queue THEY ARE EXPECTING TO RECIEVE FILES
# WE SEND AN ACK TO SIGNAL THE CLIENT WE ARE READY FOR THE NEXT PAYLOAD

def close_sockets(sockets):
	''' Helper to close all connections when an error ocurrs or a Interrupt

		Args:
			sockets(list): Contains a list of open sockets
	'''
	for sock in sockets:
		sock.close()


def main(ip=SERVER_HOST, port=SERVER_PORT):
	print(f"ESTABLISHING CONNECTION ON {ip} {port}")
	handle_conn(ip, port)


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
					print("TODO verbose")
				elif o == "-d":
					print("TODO default")
				elif o == "-w":
					sleep = True
				elif o == "-r":
					remove_temp = True
				elif o == "-i":
					if len(args) == 1:
						main(ip=a, port=int(args[0]))
					else:
						print("Error 2 arguments are required")
						usage(prog)
						sys.exit()
				else:
					assert False, "unhandled option"

		except getopt.GetoptError as err:
			print(err)
			usage(prog)
		