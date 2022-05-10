#!/usr/bin/env python3

import parse_rakefile
import sys
import socket
import select
import subprocess
import os
import time
import random

# DEFAULT PORT AND HOSTS
SERVER_PORT = 50009
#SERVER_HOST = '192.168.1.105'
SERVER_HOST = '127.0.0.1'
# MAX SIZE OF BLOCKS WHEN READING IN STREAM DATA
MAX_BYTES = 1024
# THE STANDARD THIS PROGRAM WILL USE TO ENCODE AND DECODE STRINGS
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
TIMEOUT 		= 0.5
# INTS OR ACKS ARE 8 BYTES LONG
MAX_BYTE_SIGMA = 8
# USE BIG BIG_EDIAN FOR BYTE ORDER
BIG_EDIAN = 'big'

# ACKS INTEGERS ARE 8 BYTES LONG
MAX_BYTE_SIGMA = 8

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
		self.CMD_BYTE_FILE = 5
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

# INIT GLOBALS
# INIT ENUM CLASS
ACK = Ack()
cost_list = list()

def usage():
	print("Usage: ")


def create_socket(host, port):
	''' creates connections to given hosts on give port

		Args:
			host(str): Represents the address or ip
			port(int): port number to connect on

		Returns:
			sd(socket): The connection object
	
	'''
	try:
		sd = socket.socket()
		print( f"Socket succesfully created! ({host}:{port})" )
		print( f'connecting to {host}:{port}...' )
		sd.connect( (host, port) )
	except socket.error as err:
		if err.errno == 111:
			sys.exit( ( f'Connection refused with error: {err}' ) )
		else: 
			sys.exit( f'socket creation failed with error: {err}' )

	return sd


def close_sockets(sockets):
	''' Helper to close all connections when an error ocurrs or a Interrupt

		Args:
			sockets(list): Contains a list of open sockets
	'''
	for sock in sockets:
		sock.close()


def send_datagram(sd, ack_type, payload=None):
	''' Helper to build the datagram

		Args;
			sd(socket): connection to send the datagram
			ack_type(int): Represents the acknowledgment type
	
	'''
	sigma = ack_type.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)

	if ack_type == ACK.CMD_QUOTE_REQUEST:
		print("SENDING ACK FOR COST REQUEST ---->")
		sd.sendall( sigma )
	
	elif ack_type == ACK.CMD_EXECUTE:
		print(f'SENDING ACK FOR EXECUTE ---->')
		sd.sendall( sigma )
		sd.sendall(f'{payload}'.encode(FORMAT))

# TODO: DONT MAKE cost_list global but instead have it sent in 
# as a paramter
def get_lowest_cost():
	'''	Chooses the best or cheapest server to continue execution

		Returns:
			result(tuple): (str):hostname, (int):port
	'''
	global cost_list
	lowest_cost = sys.maxsize
	result = tuple()

	for i in cost_list:
		if i[0] < lowest_cost:
			lowest_cost = i[0]
			result = i[1]

	return result


def add_cost_tuple(sd, cost):
	''' Helper to record current 'bids' or cost from servers to continue 
		execution with them.

		Args:
			sd(socket): Socket object with stats
			cost(int): the bid from the server
	'''
	global cost_list
	ip_port = sd.getpeername()
	cost_list.append((cost, ip_port))


def send_size(sd, filename):
	''' Send file size to server. This function will use system calls
		to find the file and return the size in bytes
	
		Args:
			sd(socket): Connection to send the filename
			filename(str): name of the file we want to send the size of.
	'''
	sigma = ACK.CMD_SEND_SIZE.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	size = os.path.getsize(f'./{filename}')
	payload = size.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( sigma )
	sd.sendall( payload )


def send_file_name(sd, filename):
	''' Send filename to server
	
		Args:
			sd(socket): Connection to send the filename
			filename(str): Name of file to send
	'''
	print(f'SENDING FILENAME ({filename})...')
	sigma = ACK.CMD_SEND_NAME.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( sigma )

	payload = filename.encode(FORMAT)
	size = len(payload).to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	# SEND THE LENGTH TO EXPECT
	sd.sendall( size )
	sd.sendall( payload )



def send_req_file(sd, filename):
	''' Send file contents to server

		Args:
			sd(socket): Connection to send the filename
			filename(str): Name of file to transfer
	'''
	print(f'SENDING FILE ---->')
	with open(filename, "r") as f:
		sigma = ACK.CMD_SEND_FILE.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
		payload = f.read()
		sd.sendall( sigma )
		sd.sendall( payload.encode(FORMAT) )


# TODO: some files being sent by the client maybe binary files use this
def send_byte_file(sd, filename):
	''' Transfer binary file
	
		Args:
			sd(socket): Connection to send the file
			file_attr(FileStat Oject): Object contains the file stats
	'''
	print(f'<-------SENDING FILE')
	sigma = ACK.CMD_BYTE_FILE.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( sigma )
	
	#payload = b''
	with open(filename, 'rb') as f:
		payload = f.read()

	sd.sendall( payload )
	print(f'FILE SENT...')


def write_file(sd, filename, size):
	''' Receive binary file from server
		Args:
			sd(socket): Connection file is being sent from
			filename(str): Name of file
			size(int): Total size of the file being received in bytes
			sd(socket): Connection to send the file
			file_attr(FileStat Oject): Object contains the file stats
	'''
	print("ENETERED write mode")
	path = f'./{filename}'
	try:
		with open(path, "wb") as f:
			buffer = b""
			while len(buffer) < size:
				buffer += sd.recv(MAX_BYTES)

			f.write(buffer)

	except OSError as err:
		sys.exit(f'File creation failed with error: {err}')


#TODO: dont need ack type args
def send_ack(sd, ack_type):
	'''Helper sends acknowledgments to a connection
	
		Args:
			sd(socket): Connection to send the acknowledgment
			ack_type(int): integer representing the acknowledgment type
	'''
	print(f'----> SENDING ACK')
	
	# SEND ACK WITH FIXED BYTE ORDER AND SIZE
	ack = ack_type.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( ack )


def execute(sd, ack_type, cmd=None):
		# SOCKETS WE EXPECT TO READ FROM
		input_sockets = []

		# SOCKETS WE EXPECT TO WRITE TO
		output_sockets  = []

		# OUTGOING MESSAGE QUEUES
		msg_queue = {}

		# KEEP TRACK OF SOCKETS NEEDING ACKS
		ack_queue = {}

		# TRACK FILES TO EXPECT
		file_to_recv = {}

		# TRACK SIZE OF FILE TO EXPECT
		file_size = {}

		file_count = 0

		if ack_type == ACK.CMD_QUOTE_REQUEST:
			for s in sd:
				msg_queue[s] = ACK.CMD_QUOTE_REQUEST
				output_sockets.append(s)
				s.setblocking(False)
		
		if ack_type == ACK.CMD_EXECUTE:
			msg_queue[sd] = ACK.CMD_EXECUTE
			output_sockets.append(sd)
			sd.setblocking(False)

		if ack_type == ACK.CMD_SEND_NAME:
			msg_queue[sd] = ACK.CMD_SEND_NAME
			# TRACK HOW MANY FILES TO SEND
			file_count = len(cmd.requires)-1 # -1 because first index is the requires string
			output_sockets.append(sd)
			sd.setblocking(False)
		

		while msg_queue:
			try:
				
				# GET THE LIST OF READABLE SOCKETS
				read_sockets, write_sockets, error_sockets = select.select(input_sockets, output_sockets, [], TIMEOUT)

				for sock in read_sockets:
					if sock:
						print("WAITING FOR REPLY...")
						if sock in input_sockets:
							input_sockets.remove(sock)

						# SOMETHING TO READ
						datagram = b''
						while len(datagram) < 8:
							more_size = sock.recv( MAX_BYTE_SIGMA - len(datagram) )
							if not more_size:
								raise Exception("Short file length received")

							datagram += more_size
						
						sigma = int.from_bytes(datagram, BIG_EDIAN)
						
						print(f"RECIEVED ACK TYPE {sigma}")
						# RECIEVED ACK THAT LAST DATAGRAM WAS RECIEVED
						# NOW SEND THE NEXT PAYLOAD
						if sigma == ACK.CMD_ACK:
							output_sockets.append(sock)

						elif sigma == ACK.CMD_QUOTE_REPLY:
							cost = sock.recv(MAX_BYTE_SIGMA)
							cost = int.from_bytes(cost, BIG_EDIAN)
							print(f"RECIEVED COST: {cost}")
							add_cost_tuple(sock, cost)
							del msg_queue[sock]
							print("CLOSING CONNECTION...")
							sock.close()
								
						elif sigma == ACK.CMD_RETURN_STATUS:
							r_code = sock.recv(MAX_BYTES)
							r_code = int.from_bytes(r_code, BIG_EDIAN)
							print(f"RECIEVED STATUS CODE: {r_code}")

							# EXECUTION WAS SUCCESSFUL, ON SUCCESS A FILE SHOULD BE SENT FROM SERVER
							if r_code == 0:
								# EXPECT A FILE SENT FROM SERVER
								msg_queue[sock] = ACK.CMD_SEND_NAME
								
							# EXECUTION FAILED WITH WARNING
							#TODO: handle error codes
							elif 0 < r_code < 5:
								print("REVIEVCED A WARNING ERROR")
								msg_queue[sock] = ACK.CMD_RETURN_STDOUT

							# EXECUTION HAD A FATAL ERROR
							else:
								print("REVIEVCED A FATAL ERROR")
								msg_queue[sock] = ACK.CMD_RETURN_STDERR

							# SEND ACKS 
							ack_queue[sock] = True
							output_sockets.append(sock)

						elif sigma == ACK.CMD_SEND_NAME:
							payload = sock.recv(MAX_BYTES).decode(FORMAT)
							file_to_recv[sock] = payload
							msg_queue[sock] = ACK.CMD_SEND_SIZE
							ack_queue[sock] = True
							output_sockets.append(sock)

						elif sigma == ACK.CMD_SEND_SIZE:
							payload = sock.recv(MAX_BYTE_SIGMA)
							file_size[sock] = int.from_bytes(payload, BIG_EDIAN)
							msg_queue[sock] = ACK.CMD_SEND_FILE
							ack_queue[sock] = True
							output_sockets.append(sock)
						
						elif sigma == ACK.CMD_SEND_FILE:
							print("RECIEVING FILE")
							write_file(sock, file_to_recv[sock], file_size[sock])
							del file_to_recv[sock]
							del file_size[sock]
							print("CLOSING CONNECTION...")
							sock.close()
							del msg_queue[sock]
							# END OF CONNECTION 
							
				for sock in write_sockets:
					if sock:
						if sock in output_sockets:
							output_sockets.remove(sock)

						# CHECK WHAT YPE OF MSG TO SEND
						msg_type = msg_queue[sock]
						print(f"SENDING MESSAGE TYPE: {msg_type}")

						# SLEEP
						# rand = random.randint(1, 10)
						# timer = os.getpid() % rand + 2
						# #print( f'sleep for: {timer}' )
						# time.sleep(timer)

						# WHEN SOCKETS ARE IN ack_queue THEY ARE EXPECTING TO RECIEVE FILES
						# WE SEND AN ACK TO SIGNAL THE SERVER WE ARE READY FOR THE NEXT PAYLOAD
						if sock in ack_queue:
							send_ack(sock, ACK.CMD_ACK)
							input_sockets.append(sock)
							del ack_queue[sock]

						# SEND AN ACK FOR A QUOTE
						elif msg_type == ACK.CMD_QUOTE_REQUEST:
							send_datagram(sock, msg_type)
							msg_queue[sock] = ACK.CMD_QUOTE_REQUEST
							input_sockets.append(sock)

						elif msg_type == ACK.CMD_SEND_NAME:
							# NAME OF FILE TO SEND
							index = file_count
							data = cmd.requires[index]
							print(file_count)
							print(data)

							# WHEN WE HAVE SENT ALL THE FILES WE NOW WANT TO SEND A COMMAND TO EXECUTE
							if file_count == 0:
								send_datagram(sd, ACK.CMD_EXECUTE, cmd.cmd)
								# WHEN THEN WAIT FOR THE RETURN STATUS
								msg_queue[sock] = ACK.CMD_RETURN_STATUS
							# ELSE WE HAVE MORE FILES TO SEND
							else:
								send_file_name(sd, data)
								msg_queue[sock] = ACK.CMD_SEND_SIZE
							input_sockets.append(sock)
						
						elif msg_type == ACK.CMD_SEND_SIZE:
							index = file_count
							filename = cmd.requires[index]
							send_size(sd, filename)
							msg_queue[sock] = ACK.CMD_SEND_FILE
							input_sockets.append(sock)

						elif msg_type == ACK.CMD_SEND_FILE:
							index = file_count
							filename = cmd.requires[index]
							send_req_file(sd, filename)
							# DECREMENT THE FILE COUNT
							file_count -= 1
							# GET READY TO SEND THE NEXT FILE
							msg_queue[sock] = ACK.CMD_SEND_NAME
							input_sockets.append(sock)

						# MAIN PROG WILL CALL THIS IF NO REQUIRED FILES ARE NEEDED
						elif msg_type == ACK.CMD_EXECUTE:
							send_datagram(sd, ACK.CMD_EXECUTE, cmd.cmd)
							msg_queue[sock] = ACK.CMD_RETURN_STATUS
							input_sockets.append(sock)

			except KeyboardInterrupt:
				print('Interrupted. Closing sockets...')
				# MAKE SURE WE CLOSE SOCKETS GRACEFULLY
				close_sockets(input_sockets)
				close_sockets(output_sockets)
				sys.exit()
			except Exception as err:
				print( f'ERROR occurred in {execute.__name__} with code: {err}' )
				close_sockets(input_sockets)
				close_sockets(output_sockets)
				sys.exit()
	

def get_all_conn(hosts):
	socket_lists = list()
	for key in hosts:
		socket_lists.append(create_socket(key, int(hosts[key])))
		print(key, hosts[key])
	
	return socket_lists


def main(argv):
	hosts, actions = parse_rakefile.read_rake(argv[1])

	for sets in actions:
		# ADDRESS OF LOWEST BID
		slave_addr = tuple()
		for command in sets:
			# DO WE RUN THIS COMMAND LOCAL OR REMOTE
			if not command.remote:
				subprocess.run(command.cmd, shell=True)
			# IS A REMOTE COMMAND
			else:
				# GET THE LOWEST COST
				sockets_list = get_all_conn(hosts)
				execute(sockets_list, ACK.CMD_QUOTE_REQUEST)

				slave_addr = get_lowest_cost()
				print(slave_addr)
				# EXECUTE COMMANNDS WITH THIS SOCKET
				slave = create_socket(slave_addr[0], slave_addr[1])

				print(command.requires)
				# IF FILES ARE REQUIRED TO RUN THE COMMAND SEND THE FILES FIRST
				if len(command.requires) > 0:
					execute(slave, ACK.CMD_SEND_NAME, command)
				# ELSE JUST RUN THE COMMAND	
				else:
					execute(slave, ACK.CMD_EXECUTE, command)
		
if __name__ == "__main__":
	main(sys.argv)
