#!/usr/bin/env python3

import parse_rakefile
import sys
import socket
import select
import subprocess
import os
import time
import random

SERVER_PORT = 50009
#SERVER_HOST = '192.168.1.105'
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'
TIMEOUT 		= 0.5

class Ack:
	def __init__(self):
		self.CMD_ECHO 			= 0
		self.CMD_ECHOREPLY 		= 1

		self.CMD_QUOTE_REQUEST 	= 2
		self.CMD_QUOTE_REPLY 	= 3

		self.CMD_SEND_REQIUREMENTS	= 4
		self.CMD_FILE_COUNT		= 5
		self.CMD_SEND_FILE	 	= 6
		self.CMD_SEND_SIZE		= 7
		self.CMD_SEND_NAME		= 8

		self.CMD_EXECUTE_REQ 	= 9
		self.CMD_EXECUTE 		= 10
		self.CMD_RETURN_STATUS 	= 11

		self.CMD_RETURN_STDOUT 	= 12
		self.CMD_RETURN_STDERR 	= 13

		self.CMD_RETURN_FILE 	= 14

		self.CMD_ACK 			= 15

# INIT GLOBALS
# init enum class
ACK = Ack()

cost_list = list()

def usage():
	print("Usage: ")


def create_socket(host, port):
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
	for sock in sockets:
		sock.close()


def send_datagram(sd, ack_type, payload=None):
	sigma = str(ack_type)

	if ack_type == ACK.CMD_QUOTE_REQUEST:
		print("SENDING ACK FOR COST REQUEST ---->")
		sd.send(sigma.encode(FORMAT))
	
	elif ack_type == ACK.CMD_EXECUTE:
		print(f'SENDING ACK FOR EXECUTE ---->')
		sd.send(f'{sigma} {payload}'.encode(FORMAT))


def get_lowest_cost():
	global cost_list
	lowest_cost = sys.maxsize
	result = tuple()

	for i in cost_list:
		if i[0] < lowest_cost:
			lowest_cost = i[0]
			result = i[1]

	return result


def add_cost_tuple(sd, cost):
	global cost_list
	ip_port = sd.getpeername()
	cost_list.append((cost, ip_port))


def send_size(sd, filename):
	sigma = str(ACK.CMD_SEND_SIZE)
	size = os.path.getsize(f'./{filename}')
	payload = str(size)
	sd.send(f'{sigma} {payload}'.encode(FORMAT))


def send_file_name(sd, filename):
	print(f'SENDING FILENAME ({filename})...')
	sigma = str(ACK.CMD_SEND_NAME)
	sd.send(f'{sigma} {filename}'.encode(FORMAT))


def send_req_file(sd, filename):
	print(f'SENDING FILE ---->')
	with open(filename, "r") as f:
		sigma = ACK.CMD_SEND_FILE
		payload = f.read()
		payload = f"{sigma} {payload}"
		sd.send(payload.encode(FORMAT))


def write_file(sd, filename, size, data):
	path = f'./{filename}'
	try:
		with open(path, "ab") as f:
			f.write(data)
			current = os.path.getsize(path)
			size_left = current - size

			while size_left > 0:
				f.write(sd.recv(MAX_BYTES))
				size_left -= MAX_BYTES

	except OSError as err:
		sys.exit(f'File creation failed with error: {err}')



#TODO: dont need ack type args
def send_ack(sd, ack_type):
	print(f'<---- SENDING ACK')
	ack = str(ack_type)
	sd.send( ack.encode(FORMAT) )


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
						datagram = sock.recv( MAX_BYTES ).decode( FORMAT ).split()
						sigma = int(datagram[0])
						
						# RECIEVED ACK THAT LAST DATAGRAM WAS RECIEVED
						# NOW SEND THE NEXT PAYLOAD
						if sigma == ACK.CMD_ACK:
							output_sockets.append(sock)

						elif sigma == ACK.CMD_QUOTE_REPLY:
							cost = int(datagram[1])
							print(f"RECIEVED COST: {cost}")
							add_cost_tuple(sock, cost)
							del msg_queue[sock]
							sock.close()
								
						elif sigma == ACK.CMD_RETURN_STATUS:
							r_code = int(datagram[1])
							print(f"RECIEVED STATUS CODE: {r_code}")

							# EXECUTION WAS SUCCESSFUL, ON SUCCESS A FILE SHOULD BE SEND FROM SERVER
							if r_code == 0:
								send_ack(sd, ACK.CMD_ACK)
								# EXPECT A FILE SENT FROM SERVER
								msg_queue[sock] = ACK.CMD_SEND_FILE
								
							# EXECUTION FAILED WITH WARNING
							#TODO: hand error codes
							elif 0 < r_code < 5:
								print("REVIEVCED A WARNING ERROR")
								send_ack(sd, ACK.CMD_ACK)
								msg_queue[sock] = ACK.CMD_RETURN_STDOUT

							# EXECUTION HAD A FATAL ERROR
							else:
								print("REVIEVCED A FATAL ERROR")
								send_ack(sd, ACK.CMD_ACK)
								msg_queue[sock] = ACK.CMD_RETURN_STDERR

							# SEND ACKS 
							ack_queue[sock] = True
							output_sockets.append(sock)

						elif sigma == ACK.CMD_SEND_NAME:
							payload = datagram[1]
							file_to_recv[sock] = payload
							msg_queue[sock] = ACK.CMD_SEND_SIZE
							ack_queue[sock] = True
							output_sockets.append(sock)

						elif sigma == ACK.CMD_SEND_SIZE:
							payload = int(datagram[1])
							file_size[sock] = payload
							msg_queue[sock] = ACK.CMD_RECV_FILE
							ack_queue[sock] = True
							output_sockets.append(sock)
						
						elif sigma == ACK.CMD_RECV_FILE:
							payload = datagram[1]
							write_file(sock, file_to_recv[sock], file_size[sock], payload)
							del filename[sock]
							del file_size[sock]
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
								# WHEN WE SEND ALL FILES WE WANT TO SEND THE EXECUTE COMMAND
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
			# except Exception as err:
			# 	print( f'ERROR occurred in {execute.__name__} with code: {err}' )
			# 	close_sockets(input_sockets)
			# 	close_sockets(output_sockets)
			# 	break
	

def get_all_conn(hosts):
	socket_lists = list()
	for key in hosts:
		socket_lists.append(create_socket(key, hosts[key]))
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
