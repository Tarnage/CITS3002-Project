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

		self.CMD_SEND_FILE	 	= 4

		self.CMD_EXECUTE_REQ 	= 5
		self.CMD_EXECUTE 		= 6
		self.CMD_RETURN_STATUS 	= 7

		self.CMD_RETURN_STDOUT 	= 8
		self.CMD_RETURN_STDERR 	= 9

		self.CMD_RETURN_FILE 	= 10

		self.CMD_ACK 			= 11

# INIT GLOBALS
# init enum class
ACK = Ack()
lowest_host = socket.socket()
lowest_port = 0
lowest_cost = sys.maxsize

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


def send_datagram(sd, ack_type, payload=''):
	if ack_type == ACK.CMD_QUOTE_REQUEST:
		print("SENDING ACK FOR COST REQUEST ---->")
		sd.send(str(ack_type).encode(FORMAT))
	
	if ack_type == ACK.CMD_EXECUTE:
		print(f'SENDING ACK FOR EXECUTE ---->')
		sd.send(str(ack_type).encode(FORMAT))

	if ack_type == ACK.CMD_RETURN_STATUS:
		print(f'SENDING COMMANDS ---->')
		sd.send(payload.encode(FORMAT))


def get_lowest_cost(sd, cost):
	global lowest_cost
	global lowest_host
	global lowest_port
	if cost < lowest_cost:
		lowest_cost = int(cost)
		lowest_host, lowest_port = sd.getpeername()


def execute(sd, ack_type, cmd=""):
		# SOCKETS WE EXPECT TO READ FROM
		input_sockets = []

		# SOCKETS WE EXPECT TO WRITE TO
		output_sockets  = []

		# OUTGOING MESSAGE QUEUES
		msg_queue = {}

		if ack_type == ACK.CMD_QUOTE_REQUEST:
			msg_queue[sd] = ACK.CMD_QUOTE_REQUEST
			output_sockets.append(sd)
		
		if ack_type == ACK.CMD_EXECUTE:
			msg_queue[sd] = ACK.CMD_EXECUTE
			output_sockets.append(sd)

		sd.setblocking(True)

		while msg_queue:
			try:
				# GET THE LIST OF READABLE SOCKETS
				read_sockets, write_sockets, error_sockets = select.select(input_sockets, output_sockets, [], TIMEOUT)

				for sock in read_sockets:
					if sock:
						if sock in input_sockets:
							input_sockets.remove(sock)

						# SOMETHING TO READ
						data = sock.recv( MAX_BYTES ).decode( FORMAT )
						msg_type = msg_queue[sock]
						print(f'LISTENING FOR REPLY TYPE: {msg_type}')
						
						if msg_type == ACK.CMD_QUOTE_REQUEST:
							if int(data) == ACK.CMD_QUOTE_REPLY:
								msg_queue[sock] = ACK.CMD_QUOTE_REPLY
								input_sockets.append(sock)
							else:
								print(f"Recieved the wrong ACK code")

						elif msg_type == ACK.CMD_QUOTE_REPLY:
							cost = data
							print(f"RECIEVED COST: {cost}")
							get_lowest_cost(sock, int(cost))
							del msg_queue[sock]
							
						
						elif msg_type == ACK.CMD_EXECUTE:
							if int(data) == ACK.CMD_ACK:
								print(f"RECIEVED ACK: {data}")
								msg_queue[sock] = ACK.CMD_RETURN_STATUS
								output_sockets.append(sock)
								
						elif msg_type == ACK.CMD_RETURN_STATUS:
							print(f"RECIEVED STATUS CODE: {data}")
							del msg_queue[sock]
							

				for sock in write_sockets:
					if sock:
						if sock in output_sockets:
							output_sockets.remove(sock)

						# CHECK WHAT YPE OF MSG TO SEND
						msg_type = msg_queue[sock]
						print(f"SENDING MESSAGE TPYE: {msg_type}")

						# SLEEP
						# rand = random.randint(1, 10)
						# timer = os.getpid() % rand + 2
						# #print( f'sleep for: {timer}' )
						# time.sleep(timer)

						# SEND AN ACK FOR A QUOTE
						if msg_type == ACK.CMD_QUOTE_REQUEST:
							send_datagram(sd, msg_type)
							msg_queue[sock] = ACK.CMD_QUOTE_REQUEST
							input_sockets.append(sock)
						
						# SEND AN ACK TO EXECUTE A COMMAND
						elif msg_type == ACK.CMD_EXECUTE:
							send_datagram(sd, msg_type)
							msg_queue[sock] = ACK.CMD_EXECUTE
							input_sockets.append(sock)
						
						# SEND THE COMMANDS
						elif msg_type == ACK.CMD_RETURN_STATUS:
							send_datagram(sd, msg_type, cmd)
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
				break
	

def get_all_conn(hosts):
	socket_lists = list()
	for key in hosts:
		socket_lists.append(create_socket(key, hosts[key]))
		print(key, hosts[key])
	
	return socket_lists


def main(argv):
	global lowest_cost
	global lowest_host
	global lowest_port
	hosts, actions = parse_rakefile.read_rake(argv[1])

	for sets in actions:
		for command in sets:
			# DO WE RUN THIS COMMAND LOCAL OR REMOTE
			if not command.remote:
				subprocess.run(command.cmd, shell=True)
			# IS A REMOTE COMMAND
			else:
				# GET THE LOWEST COST
				sockets_list = get_all_conn(hosts)
				for sock in sockets_list:
					execute(sock, ACK.CMD_QUOTE_REQUEST)

				# print(lowest_host, lowest_port)
				slave = create_socket(lowest_host, lowest_port)
				# EXECUTE COMMAND ON THE LOWEST BID
				execute(slave, ACK.CMD_EXECUTE, command.cmd)
		
		# RESET lowest VARS
		lowest_host = socket.socket()
		lowest_port = 0
		lowest_cost = sys.maxsize


if __name__ == "__main__":
	main(sys.argv)
