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
		self.CMD_RESEND_FILE = 17


class Hosts:
	def __init__(self, sock, ip, port, used=False, action=None, cost=MAX_INT, got_cost=False, local=False):
		self.sock = sock
		self.ip = ip
		self.port = port
		self.used = used
		self.action = action
		self.cost = cost
		self.local = local
		self.got_cost = got_cost
		self.seq = 0
		self.recv_seq = 0
		self.curr_act = 0


# INIT GLOBALS
# INIT ENUM CLASS
ACK = Ack()
obj_hosts = list()


def usage():
	print("Usage: ")


def reset_host():
	''' Helper to re init attributes
		Note that ones a ip and port are init it doesnt change through the life of the program
	
	'''
	global obj_hosts
	for h in obj_hosts:
		h.sock.close()
		h.used = False
		h.action = None
		h.cost = MAX_INT

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

	print( f"CONNECTION SUCCESSFUL" )
	sd.setblocking(True)
	return sd


def get_host_obj(hosts):
	global obj_hosts
	obj_hosts = list()
	port = parse_rakefile.get_default_port()
	# ADD LOCAL HOST
	obj_hosts.append(Hosts(None, LOCAL_HOST, port, used=True, local=True))

	for key in hosts:
		obj_hosts.append(Hosts(None, key, hosts[key]))




def close_sockets(sockets):
	''' Helper to close all connections when an error ocurrs or a Interrupt

		Args:
			sockets(list): Contains a list of open sockets
	'''
	for sock in sockets:
		sock.close()


def send_cmd(sd):
	''' Helper send command to execute on remote servers
		Args;
			sd(socket): connection to send the datagram
			ack_type(int): Represents the acknowledgment type
			payload(str): command to execute
	
	'''
	for h in obj_hosts:
		if h.sock == sd:
			payload = h.action.cmd.encode(FORMAT)
			send_ack(sd, ACK.CMD_EXECUTE)
			send_byte_int(sd, len(payload))
			sd.sendall(payload)
			break

# TODO: DONT MAKE cost_list global but instead have it sent in 
# as a paramter
def get_lowest_cost():
	'''	Chooses the best or cheapest server to continue execution

		Returns:
			result(tuple): (str):hostname, (int):port
	'''
	global obj_hosts
	lowest_cost = MAX_INT
	curr = None
	for h in obj_hosts:
		if( (h.local == False) and (h.got_cost == True) ):
			if (h.cost < lowest_cost):
				lowest_cost = h.cost
				curr = h
				
			h.got_cost = False
			h.used = False
			# RESET COST
			h.cost = MAX_INT
	
	return curr


def mark_free(sd):
	''' Helper to mark host obj as free.
		Args:
			sd(socket): Used to compare
	'''
	global obj_hosts

	for h in obj_hosts:
		if (h.sock == sd) and (not h.local == True):
			print("MARK FREE")
			h.used = False
			break

def add_cost(sd, cost):
	''' Helper to record current 'bids' or cost from servers to continue 
		execution with them.
		Will iterate over global list obj_hosts to find the right socket

		Args:
			sd(socket): Socket object with stats
			cost(int): the bid from the server
	'''
	global obj_hosts
	for h in obj_hosts:
		if h.sock == sd:
			h.cost = cost
			h.got_cost = True
			break


def get_filename(sd):
	''' Helper to get current file file count
		Args:
			sd(sock): socket

		Return:
			str: filename
			or
			None: if no more files to send
	'''
	global obj_hosts

	for h in obj_hosts:
		if h.sock == sd:
			
			index = h.curr_act
			
			if index > 0:
				#print("FILE AND INDEX {} {}".format(h.action.requires[index], index))
				if h.seq == h.recv_seq:
					file = h.action.requires[index]
					h.curr_act -= 1
				else:
					file = h.action.requires[index+1]
				return file
			else:
				return None


def check_downloads_dir():
	''' Helper to make sure temp dir exists if not create one

		Args;
			peer_dir(str): name of the directory to check
	'''
	if not os.path.isdir(DOWNLOADS):
		try:
			os.mkdir(DOWNLOADS)
		except OSError as err:
			sys.exit("Directory creation failed with error: {err}")


def send_file_name(sd, filename):
	''' Send filename to server
	
		Args:
			sd(socket): Connection to send the filename
			filename(str): Name of file to send
	'''
	print(f'{sd.getpeername()} SENDING ({filename}) ---->')

	payload = filename.encode(FORMAT)
	send_byte_int(sd, len(payload))

	# SEND THE LENGTH TO EXPECT
	sd.sendall( payload )


def send_txt_file(sd, filename, path):
	''' Send file contents to server

		Args:
			sd(socket): Connection to send the filename
			filename(str): Name of file to transfer
	'''
	sigma = ACK.CMD_SEND_FILE.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( sigma )

	payload = ""
	with open(path, "r") as f:
		payload = f.read()
	
	
	send_file_name(sd, filename)

	send_byte_int(sd, len(payload))
	sd.sendall( payload.encode(FORMAT) )



# TODO: some files being sent by the client maybe binary files use this
def send_bin_file(sd, filename, path):
	''' Transfer binary file
	
		Args:
			sd(socket): Connection to send the file
			file_attr(FileStat Oject): Object contains the file stats
	'''
	send_byte_int(sd, ACK.CMD_BIN_FILE)
	print(f"SENDING BIN FILE {filename}---->")
	payload = b''
	with open(path, 'rb') as f:
		payload = f.read()

	send_file_name(sd, filename)
	send_byte_int(sd, len(payload))
	sd.sendall( payload )
	print(f'BIN FILE SENT...')


def send_filename(sd, filename):
	sd.sendall(filename.encode(FORMAT))


# CHANGE TO RECV STRING? JUST ONE FUNC
def recv_filename(sd):

	size = recv_byte_int(sd)

	filename = b''
	more_size = b''
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
	
		

# CHANGE TO RECV STRING?
def recv_std(sd):

	print("-----> RECEIVING ERROR MSG")
	size = recv_byte_int(sd)
	filename = b''
	more_size = b''
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

def recv_bin_file(sd):
	''' Receive binary file from server
		Args:
			sd(socket): Connection file is being sent from
	'''

	filename = recv_filename(sd)

	size = recv_byte_int(sd)

	print("ENETERED WRITE MODE...")

	check_downloads_dir()

	path = f'{DOWNLOADS}/{filename}'
	try:
		with open(path, "wb") as f:
			buffer = b""
			while len(buffer) < size:
				buffer += sd.recv(size - len(buffer))

			f.write(buffer)

	except OSError as err:
		sys.exit(f'File creation failed with error: {err}')


def send_ack(sd, ack_type):
	'''Helper sends acknowledgments to a connection
	
		Args:
			sd(socket): Connection to send the acknowledgment
			ack_type(int): integer representing the acknowledgment type
	'''
	print(f'----> SENDING ACK {ack_type}')
	
	# SEND ACK WITH FIXED BYTE ORDER AND SIZE
	ack = ack_type.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall( ack )


def recv_byte_int(sd):
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
			more_size = sd.recv( MAX_BYTE_SIGMA - len(size) )
			if not more_size:
				break
		except socket.error as err:
			if err.errno == 35:
				time.sleep(0)
				continue
		size += more_size

	result = int.from_bytes(size, BIG_EDIAN)
	return result


def send_byte_int(sd, payload_len):
	''' Helper to send the byte size of outgoing payload
		Args:
			sd(socket): socket descriptor of the connection
	'''
	size = payload_len.to_bytes(MAX_BYTE_SIGMA, BIG_EDIAN)
	sd.sendall(size)


def is_bin_file(path):
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


def find_files(filename):
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
			# print(finish - start)
			return result


def incre_seq(sd):
	global obj_hosts
	for h in obj_hosts:
		if h == sd:
			h.seq = 1 - h.seq
			break

def append_recv_seq(sd, seq):
	global obj_hosts
	for h in obj_hosts:
		if h == sd:
			h.recv_seq = seq
			break


def resend_file(sd):
	global obj_hosts
	for h in obj_hosts:
		if h == sd:
			h.recv_seq = h.seq
			return True
	return False


def handle_conn(sets):
	global obj_hosts

	timer = {}

	# SOCKETS WE EXPECT TO READ FROM
	input_sockets = list()

	# SOCKETS WE EXPECT TO WRITE TO
	output_sockets  = list()

	# OUTGOING MESSAGE QUEUES
	msg_queue = dict()

	# KEEP TRACK OF SOCKETS NEEDING ACKS
	ack_queue = dict()
	
	# INDEX TO THE SET
	actions_executed = 0

	# IF CURRENT ACTION IS THE LAST ONE DONT
	# SEND OUT REQUEST FOR COSTS
	curr_action = 0

	# REMAINING ACTIONS IN THIS LOOP
	actions_left = len(sets)

	# HOW MANY SOCKETS ARE OUT REQUESTING FOR COST
	quote_queue = 0

	# ARE THERE COST TO BE CALCULATED
	cost_waiting = False

	while actions_executed < actions_left :
		try:
			# WE HAVE COSTS FOR THE NEXT ACTION

			# WE HAVE ACTIONS TO EXECUTE 
			if (curr_action < actions_left):
				if (sets[curr_action].remote == False):
					# 0TH INDEX IS ALWAYS LOCALHOST
					obj_hosts[0].action = sets[curr_action]
					
					sd = create_socket(obj_hosts[0].ip, obj_hosts[0].port)
					obj_hosts[0].sock = sd
					msg_queue[sd] = ACK.CMD_SEND_FILE
					curr_action += 1
					output_sockets.append(sd)
					# actions_executed += 1

				if (curr_action < actions_left):
					print(f"{actions_executed}  {actions_left}  {curr_action}")
					# SEND COST REQS TO FREE SERVERS
					for h in obj_hosts:
						if (h.used == False) and (h.local == False):
							sd = create_socket(h.ip, h.port)
							h.sock = sd
							h.used = True
							quote_queue += 1
							msg_queue[sd] = ACK.CMD_QUOTE_REQUEST
							output_sockets.append(sd)

			if (quote_queue == 0) and (cost_waiting == True) and (actions_executed == curr_action):
				# CHECK WHEN WE HAVE COSTS TO CALCULATE FOR NEXT COMMAND
				if sets[curr_action].remote:
					slave = get_lowest_cost()
					cost_waiting = False
					slave.action = sets[curr_action]
					slave.curr_act = len(slave.action.requires) -1
					sd = create_socket(slave.ip, slave.port)
					slave.sock = sd
					slave.used = True
					msg_queue[sd] = ACK.CMD_SEND_FILE
					curr_action += 1
					output_sockets.append(sd)

			#print_objs(obj_hosts)

			to_remove = list()
			for waiting in timer:
				curr = time.time()
				wait_time = int(curr - timer[waiting])
				if wait_time > 5:
					input_sockets.remove(waiting)
					output_sockets.append(waiting)
					to_remove.append(waiting)
			
			for remove in to_remove:
				del timer[remove]

			# GET THE LIST OF READABLE SOCKETS
			read_sockets, write_sockets, error_sockets = select.select(input_sockets, output_sockets, [], TIMEOUT)
			
			for sock in read_sockets:
				if sock:
					#print_objs(obj_hosts)
					#print(f"{sock.getpeername()} WAITING FOR REPLY...")
					if sock in input_sockets:
						input_sockets.remove(sock)

					# SOMETHING TO READ
					sigma = recv_byte_int(sock)
					
					#print(f"RECIEVED ACK TYPE {sigma}")
					# RECIEVED ACK THAT LAST DATAGRAM WAS RECIEVED
					# NOW SEND THE NEXT PAYLOAD
					if sigma == ACK.CMD_ACK:
						seq = recv_byte_int(sock)
						append_recv_seq(sock, seq)
						output_sockets.append(sock)

					elif sigma == ACK.CMD_QUOTE_REPLY:
						cost = recv_byte_int(sock)
						print(f"RECIEVED COST: {cost}")
						add_cost(sock, cost)
						del msg_queue[sock]
						cost_waiting = True
						quote_queue -= 1
						print("CLOSING CONNECTION...")
						#sock.close()

					elif sigma == ACK.CMD_RETURN_STATUS:
						r_code = recv_byte_int(sock)
						print(f"RECV CODE: {r_code}")

						# EXECUTION WAS SUCCESSFUL, ON SUCCESS A FILE SHOULD BE SENT FROM SERVER
						if r_code == 0:
							# EXPECT A FILE SENT FROM SERVER
							print(f"EXECUTION ON REMOTE HOST WAS SUCCESSFUL!!")
							msg_queue[sock] = ACK.CMD_RETURN_FILE
							input_sockets.append(sock)
							
					# EXECUTION FAILED WITH WARNING
					#TODO: handle error codes
					elif sigma == ACK.CMD_RETURN_STDOUT:
						print("REVIEVCED A WARNING ERROR")
						code = recv_byte_int(sock)
						msg = recv_std(sock)
						raise Exception(msg)
						
					# EXECUTION HAD A FATAL ERROR
					elif sigma == ACK.CMD_RETURN_STDERR:
						print("REVIEVCED A FATAL ERROR")
						code = recv_byte_int(sock)
						msg = recv_std(sock)
						raise Exception(msg)
						
					elif sigma == ACK.CMD_RETURN_FILE:
						print("<----- RECIEVING FILE...")
						recv_bin_file(sock)
						print("CLOSING CONNECTION...")
						actions_executed = actions_executed + 1
						mark_free(sock)
						#sock.close()
						del msg_queue[sock]
						# END OF CONNECTION 

					elif sigma == ACK.CMD_NO_OUTPUT:
						r_code = recv_byte_int(sock)
						print(f"<------ RECV CODE: {r_code}")
						actions_executed = actions_executed + 1
						mark_free(sock)
						#sock.close()
						del msg_queue[sock]
						
			for sock in write_sockets:
				if sock:
					if sock in output_sockets:
						output_sockets.remove(sock)
					#print_objs(obj_hosts)
					# CHECK WHAT YPE OF MSG TO SEND
					msg_type = msg_queue[sock]
					#print(msg_queue)
					#print(f"{sock.getpeername()} SENDING MESSAGE ----->")

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
						send_ack(sock, ACK.CMD_QUOTE_REQUEST)
						msg_queue[sock] = ACK.CMD_QUOTE_REQUEST
						input_sockets.append(sock)

					elif msg_type == ACK.CMD_SEND_FILE:
						# NAME OF FILE TO SEND
						filename = get_filename(sock)
						# WHEN WE HAVE SENT ALL THE FILES WE NOW WANT TO SEND A COMMAND TO EXECUTE
						if filename == None:
							print(f'SENDING ACK FOR EXECUTE ---->')
							send_cmd(sock)
							# WHEN THEN WAIT FOR THE RETURN STATUS
							msg_queue[sock] = ACK.CMD_RETURN_STATUS
							input_sockets.append(sock)
						# ELSE WE HAVE MORE FILES TO SEND
						else:
							path = find_files(filename)
							if path != None:
								if resend_file(sock):
									send_byte_int(sock, ACK.CMD_RESEND_FILE)
								else:
									incre_seq(sock)

								if is_bin_file(path):
									send_bin_file(sd, filename, path)
								else:
									send_txt_file(sd, filename, path)
								msg_queue[sock] = ACK.CMD_SEND_FILE

								timer[sock] = time.time()

								input_sockets.append(sock)
							else:
								print(f"{filename} DOES NOT EXSIST!")
								del msg_queue[sock]
								#sock.close()


		except KeyboardInterrupt:
		# 	print('Interrupted. Closing sockets...')
		# 	# MAKE SURE WE CLOSE SOCKETS GRACEFULLY
		# 	close_sockets(input_sockets)
		# 	close_sockets(output_sockets)
		 	sys.exit()

		# except Exception as err:
		# 	print( f'ERROR IN REMOTE HOST WITH:' )
		# 	print( f'{err}' )
		# 	close_sockets(input_sockets)
		# 	close_sockets(output_sockets)
		# 	sys.exit()



def print_objs(hosts):

	for host in hosts:
		if host.action != None:
			print("ip:{}\n port:{}\n used:{}\n cmd:{}\n cost:{}\n local:{}".format(host.ip, host.port, host.used, host.action.cmd, host.cost, host.local))
		else:
			print("ip:{}\n port:{}\n used:{}\n cost:{}\n local:{}".format(host.ip, host.port, host.used, host.cost, host.local))

def main(argv):
	#dict_hosts, actions = parse_rakefile.read_rake(argv[1])
	dict_hosts, actions = parse_rakefile.read_rake("/home/thanh/GitHub/CITS3002-Project/rake-p/hardtest")
	get_host_obj(dict_hosts)
	
	for sets in actions:
		handle_conn(list(sets))
		
if __name__ == "__main__":
	main(sys.argv)
