#!/usr/bin/env python3

import getopt
import shutil
import time
import random
import os
import socket
import select
import sys
import subprocess

# DEFAULT PORSTS AND HOSTS
SERVER_PORT = 50008
#SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_HOST = '127.0.0.1'
# MAX SIZE OF BLOCKS WHEN READING IN STREAM DATA
MAX_BYTES = 1024
# THE STANDARD THIS PROGRAM WILL USE TO ENCODE AND DECODE STRINGS
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
TIMEOUT 		= 0.5
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


class FileStats():
	''' Class to help track files on the server created by the client
	
	'''
	def __init__(self, filename, size, path):
		self.filename = filename
		self.size = size
		self.path = path

# INIT ENUM CLASS
ACK = Ack()

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
	send_ack(sd, ACK.CMD_QUOTE_REPLY)
	cost = calculate_cost()
	print(f'<---- SENDING QUOTE: {cost}')
	cost = cost.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( cost )


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
	p = subprocess.run(cmd, shell=True, cwd=dir)
	print(f'COMMAND FINISHED...')

	file_attr = scan_dir(f'./tmp/{peer_dir}')

	return p.returncode, file_attr


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


def send_ack(sd, ack_type):
	'''Helper sends acknowledgments to a connection
	
		Args:
			sd(socket): Connection to send the acknowledgment
			ack_type(int): integer representing the acknowledgment type
	'''
	print(f'<---- SENDING ACK')
	sd.sendall( ack_type.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN) )


def send_filename(sd, file_attr):
	''' Send filename to client
	
		Args:
			sd(socket): Connection to send the filename
			file_attr(FileStat Oject): Object contains the file stats
	'''
	sigma = ACK.CMD_SEND_NAME.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	payload = file_attr.filename
	sd.sendall( sigma )
	sd.sendall(payload.encode(FORMAT))

# TODO: add sleep for slow connections
def recv_filename(sd):

	size = recv_byte_int(sd)
	filename = b''
	while len(filename) < size:
		try:
			more_size = sd.recv( size - len(filename) )
			if not more_size:
				time.sleep(0)
		except socket.error as err:
			if err.errno == 35:
				time.sleep(0)
				continue

		filename += more_size
	
	return filename.decode(FORMAT)



def send_file_size(sd, file_attr):
	''' Send file size to client
	
		Args:
			sd(socket): Connection to send the filename
			file_attr(FileStat Oject): Object contains the file stats
	'''
	sigma = ACK.CMD_SEND_SIZE.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	size = file_attr.size
	payload = size.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( sigma )
	sd.sendall( payload )


def send_bin_file(sd, file_attr):
	''' Transfer binary file
	
		Args:
			sd(socket): Connection to send the file
			file_attr(FileStat Oject): Object contains the file stats
	'''
	print(f'<-------SENDING FILE')
	filename = file_attr.path
	sigma = ACK.CMD_RETURN_FILE.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( sigma )

	send_file_size(sd, len(filename))
	
	#payload = b''
	with open(filename, 'rb') as f:
		payload = f.read()

	sd.sendall( payload )
	print(f'FILE SENT...')


def recv_byte_int(sd):
	''' Helper to get the size of incoming payload
		Args:
			sd(socket): socket descriptor of the connection

		Return:
			result(int): The size of incoming payload
	'''
	size = b''
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


def send_byte_size(sd, payload_len):
	''' Helper to send the byte size of outgoing payload
		Args:
			sd(socket): socket descriptor of the connection
	'''
	size = payload_len.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.send(size)


def recv_cmd(sd, size):
	''' Helper to get the size of incoming payload
		Args:
			sd(socket): socket descriptor of the connection
			size(int): the size of bytes to expect

		Return:
			result(str): The command sent from client
	'''
	payload = b''
	while len(payload) < size:
		try:
			more_size = sd.recv( size - len(payload) )
			if not more_size:
				raise Exception("Short file length received")
		except socket.error as err:
			if err.errno == 35:
				time.sleep(0)
				continue
		payload += more_size

	result = payload.decode(FORMAT)
	print("returned result")
	return result


def handle_conn(host, port):
	'''Non Blocking server version, server will continuously poll the socket for a connection
		
		Args:
		host (str): the ip address the server will bind
		port (int): the port the server will bind 
	'''	

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
	sd.setblocking(False)

	# SOCKETS WE EXPECT TO READ FROM
	input_sockets = [sd]
	# SOCKETS WE EXPECT TO WRITE TO
	output_sockets  = []
	# OUTGOING MESSAGE QUEUES
	# TRACKS WHAT ACKS SOCKETS ARE WAITING FOR
	msg_queue = {}

	# KEEP TRACK OF SOCKETS NEEDING ACKS
	ack_queue = {}

	# STORE FILE NAMES WE ARE EXPECTING TO RECV
	filename = {}

	# STORE FILE SIZES WE ARE EXPECTING TO RECV
	file_size = {}

	# STORE RETURN CODES
	return_code = {}

	# STORE FILES WE NEED TO SEND BACK TO CLIENT 
	file_to_send = {}

	while True:

		try:
			# GET THE LIST OF READABLE SOCKETS
			read_sockets, write_sockets, _ = select.select(input_sockets, output_sockets, [], TIMEOUT)

			for sock in read_sockets:
				print("Reading...")
				if sock == sd:
					# ESTABLISH CONNECTION WITH CLIENT
					conn, addr = sd.accept()

					# ADD CONECTION TO LIST OF SOCKETS
					input_sockets.append(conn)
					print(f'CONNECTED TO :{addr}')

				else:
					# REMOVE SOCKET FROM INPUT SOCKETS LIST
					# AS WE CONNECT TO IT

					if sock in input_sockets:
						input_sockets.remove(sock)
						
					# SOMETHING TO READ
					sigma = recv_byte_int(sock)
					# RECIEVED ACK THAT LAST DATAGRAM WAS RECIEVED
					# NOW SEND THE NEXT 
					if sigma == ACK.CMD_ACK:
						print("ACK RECIEVED")
						output_sockets.append(sock)

					# ELSE THE INITIAL CONNECTION REQUEST 
					elif sigma > 0:

						print(f"----> RECIEVING ACK TYPE: {sigma}")

						# REQUEST FOR COST QUOTE
						if sigma == ACK.CMD_QUOTE_REQUEST:
							print(f'COST QUOTE REQUESTED')
							# TRACK WHAT THIS WILL DO NEXT
							msg_queue[sock] = sigma
							# PREPARE IT FOR WRITING
							output_sockets.append(sock)
						
						# REQUEST TO RUN COMMAND
						elif sigma == ACK.CMD_EXECUTE:
							size = recv_byte_int(sock)
							payload = recv_cmd(sock, size)
							print(f'REQUEST TO EXECUTE...{payload}')
							# STORE RETURN CODE IN DICT 
							r_code, file_attr = run_cmd(sock, payload)
							file_to_send[sock] = file_attr
							return_code[sock] = r_code
							msg_queue[sock] = ACK.CMD_RETURN_STATUS
							output_sockets.append(sock)

						# RECEIVE FILE NAME
						# elif sigma == ACK.CMD_SEND_NAME:
						# 	filename[sock] = recv_filename(sock)
						# 	msg_queue[sock] = ACK.CMD_SEND_SIZE
						# 	ack_queue[sock] = True
						# 	output_sockets.append(sock)

						# elif sigma == ACK.CMD_SEND_SIZE:
						# 	payload = sock.recv(MAX_BYTES)
						# 	payload = int.from_bytes(payload, BIG_EDIAN)
						# 	print(f"RECIEVED SIZE {payload}")
						# 	file_size[sock] = payload
						# 	msg_queue[sock] = ACK.CMD_SEND_FILE
						# 	ack_queue[sock] = True
						# 	output_sockets.append(sock)
						
						elif sigma == ACK.CMD_SEND_FILE:
							recv_text_file(sock)
							msg_queue[sock] = ACK.CMD_EXECUTE
							ack_queue[sock] = True
							output_sockets.append(sock)

					# INTERPRET EMPTY RESULT AS CLOSED CONNECTION
					else:
						print(f'Closing connections')
						if sock in output_sockets:
							output_sockets.remove(sock)
						if sock in input_sockets:
							input_sockets.remove(sock)
						sock.close()

			for sock in write_sockets:
				if sock:
					print("Sending...")
					# REMOVE CURRENT SOCKET FROM WRITING LIST
					if sock in output_sockets:
						output_sockets.remove(sock)

					# WHAT TYPE OF MSG IS THIS SOCKET SENDING
					msg_type = msg_queue[sock]

					# SLEEP
					if sleep == True:
						rand = random.randint(1, 10)
						timer = os.getpid() % rand + 2
						print( f'sleep for: {timer}' )
						time.sleep(timer)

					# WHEN SOCKETS ARE IN ack_queue THEY ARE EXPECTING TO RECIEVE FILES
					# WE SEND AN ACK TO SIGNAL THE CLIENT WE ARE READY FOR THE NEXT PAYLOAD
					if sock in ack_queue:
						send_ack(sock, ACK.CMD_ACK)
						input_sockets.append(sock)
						del ack_queue[sock]

					# SEND ACK, THAT AFTER THIS I WILL SEND QUOTE
					elif msg_type == ACK.CMD_QUOTE_REQUEST:
						send_quote(sock)
						del msg_queue[sock]
						# SEND REPLY AND CLOSE THE CONNECTION
						print(f"CLOSING CONNECTION WITH {sock.getpeername()}")
						sock.close()
					
					elif msg_type == ACK.CMD_RETURN_STATUS:
						r_code = return_code[sock]
						print(f"<-------- SENDING RETURN STATUS ({r_code})")

						# EXECUTION WAS SUCCESSFUL, NOW WE GET READY TO SEND THE OUTPUT FILE
						if r_code == 0:
							sigma = ACK.CMD_RETURN_STATUS.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
							payload = r_code.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
							sock.sendall( sigma )
							sock.sendall( payload )

							# TODO: THIS FUNCTION DOESNT LIKE TO BE CALLED
							# SEEMS LIKE CONNECTION GETS CLOSED BEFORE WE CAN SEND DATA
							# COULD BE A NON BLOCKING / SELECT() ISSUE
							#send_return_status(sock)

							msg_queue[sock] = ACK.CMD_RETURN_FILE
						# EXECUTION FAILED WITH WARNING
						#TODO: hand error codes
						elif 0 < r_code < 5:
							pass
						# EXECUTION HAD A FATAL ERROR
						else:
							pass

						input_sockets.append(sock)
						
					# THE ONLY FILES A SERVER WILL SEND IS THE LATEST CREATED IN THE tmp DIR
					# AFTER SUCCESSFUL TRANSFER THE tmp DIR SHOULD BE DELETED
					# elif msg_type == ACK.CMD_SEND_NAME:
					# 	file_attr = file_to_send[sock]
					# 	send_filename(sock, file_attr)
					# 	msg_queue[sock] = ACK.CMD_SEND_SIZE
					# 	input_sockets.append(sock)
						

					# elif msg_type == ACK.CMD_SEND_SIZE:
					# 	file_attr = file_to_send[sock]
					# 	send_file_size(sock, file_attr)
					# 	msg_queue[sock] = 6
					# 	input_sockets.append(sock)

					elif msg_type == ACK.CMD_RETURN_FILE:
						print("entered here")
						file_attr = file_to_send[sock]
						send_filename(sock, file_attr)
						send_file_size(sock, file_attr)
						send_bin_file(sock, file_attr)
						print("CLOSING CONNECTION...")
						del msg_queue[sock]
						# DELETE THE TEMP FOLDER CREATED FOR THE CLIENT
						if remove_temp == True:
							rm_client_files(sock)
						# END OF CONNECTION
						

		except KeyboardInterrupt:
			print('Interrupted. Closing sockets...')
			# Make sure we close sockets gracefully
			close_sockets(input_sockets)
			close_sockets(output_sockets)
			sys.exit()


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
		