#!/usr/bin/env python3

import time
import random
import os
import socket
import select
import sys
import subprocess
import queue

SERVER_PORT = 50008
# BEAWARE YOU MAY NEED TO EDIT /etc/hosts. TO GET PROPER LOCAL IP ADDRESS
#SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
TIMEOUT 		= 0.5

class Ack:
	def __init__(self):
		self.CMD_ECHO = 0
		self.CMD_ECHOREPLY = 1

		self.CMD_QUOTE_REQUEST = 2
		self.CMD_QUOTE_REPLY = 3

		self.CMD_SEND_FILE = 4

		self.CMD_EXECUTE_REQ = 5
		self.CMD_EXECUTE = 6
		self.CMD_RETURN_STATUS = 7

		self.CMD_RETURN_STDOUT = 8
		self.CMD_RETURN_STDERR = 9

		self.CMD_RETURN_FILE = 10
		self.CMD_ACK = 11

# init enum class
ACK = Ack()
return_code = -1


def usage():
	print("Usage: ")


def blocking_socket(host, port):
	'''Blocking verion of the socket server program
	Program will block while waiting for a connection

	Args:
		host (str): the ip address the server will bind
		port (int): the port the server will bind 
	'''	

	try:
		# AF_INET IS THE ADDRESS FAMILY IP4
		# SOCK_STREAM MEANS TCP PROTOCOL IS USED
		sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("Port succesfully created!")
	except socket.error as err:
		print( f'socket creation failed with error {err}' )

	# BIND SOCKET TO PORT
	sd.bind( (host, port) )
	print( f'Socket is binded to {port}' )

	# PUT THE SOCKET TO LISTEN MODE
	sd.listen(DEFAULT_BACKLOG)
	print( f"Socket is listening on {host}..." )
	
	while True:

		try:
			# ESTABLISH CONNECTION WITH CLIENT
			conn, addr = sd.accept()
			print( f'Got a connection from {addr}' )

			# RECIEVE DATA
			data = conn.recv(MAX_BYTES).decode(FORMAT)
			print( f'Received msg: {data}' )

			# SLEEP
			rand = random.randint(1, 10)
			timer = os.getpid() % rand + 2
			print( f'sleep for: {timer}' )
			time.sleep(timer)

			# SEND DATA BACK
			send_data = f'Thank you for connecting to {host}:{port}'
			conn.send( send_data.encode(FORMAT) )
			print( f'sending: {send_data}' )
			

		except KeyboardInterrupt:
			print('Interrupted.')
			sd.close()
			break


def calculate_cost():
	# seed for testing
	# seed(1)
	return random.randint(1, 10)


def send_quote(sd):
	cost = str(calculate_cost())
	print(f'<---- SENDING QUOTE: {cost}')
	sd.send( cost.encode(FORMAT) )


def run_cmd(cmd):
	global return_code
	print()
	print(f'RUNNING COMMAND: {cmd}')
	p = subprocess.run(cmd, shell=True)
	print(f'COMMAND FINISHED...')
	print()

	return_code = p.returncode

def send_ack(sd, ack_type):
	if ack_type == ACK.CMD_QUOTE_REPLY:
		print(f'<---- SENDING ACK: {ACK.CMD_QUOTE_REPLY}')
		ack = str(ACK.CMD_QUOTE_REPLY)
		sd.send( ack.encode(FORMAT) )
	
	if ack_type == ACK.CMD_ACK:
		print(f'<---- SENDING ACK')
		ack = str(ack_type)
		sd.send( ack.encode(FORMAT) )


def non_blocking_socket(host, port):
	'''Non Blocking server version, server will continuously poll the socket for connection
		
		Args:
		host (str): the ip address the server will bind
		port (int): the port the server will bind 
	'''	

	try:
		# AF_INET IS THE ADDRESS FAMILY IP4
		# SOCK_STREAM MEANS TCP PROTOCOL IS USED
		sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("Port succesfully created!")
	except socket.error as err:
		print( f'socket creation failed with error {err}' )

	# BIND SOCKET TO PORT
	sd.bind( (host, port) )
	print( f'Socket is binded to {port}' )

	# PUT THE SOCKET TO LISTEN MODE
	sd.listen(DEFAULT_BACKLOG)
	print( f"Socket is listening on {host}..." )
	sd.setblocking(False)
	# SOCKETS WE EXPECT TO READ FROM
	connection_list = [sd]

	# SOCKETS WE EXPECT TO WRITE TO
	output  = []

	# OUTGOING MESSAGE QUEUES
	# TRACKS WHAT ACKS SOCKETS ARE WAITING FOR
	msg_queue = {}

	while True:

		try:
			# GET THE LIST OF READABLE SOCKETS
			read_sockets, write_sockets, error_sockets = select.select(connection_list, output, [], TIMEOUT)

			for sock in read_sockets:
				print("checking connection")
				if sock == sd:
					# ESTABLISH CONNECTION WITH CLIENT
					conn, addr = sd.accept()
					print( f'Got a connection from {addr}' )
					#conn.setblocking(True)

					# ADD CONECTION TO LIST OF SOCKETS
					connection_list.append(conn)

				else:
					# REMOVE SOCKET FROM CONNECTION LIST
					# AS WE CONNECT TO IT

					if sock in connection_list:
						connection_list.remove(sock)
						
					# RECIEVE DATA
					data = sock.recv(MAX_BYTES).decode(FORMAT)

					# IF THE SOCKET IS IN THE msg_queue THEY ARE WAITING FOR A MESSAGE
					if sock in msg_queue:
						if msg_queue[sock] == ACK.CMD_EXECUTE:
							run_cmd(data)
							msg_queue[sock] = ACK.CMD_RETURN_STATUS
							print(f"after executing sock type: {msg_queue[sock]}")
							output.append(sock)

					# ELSE THE INITIAL CONNECTION REQUEST 
					elif data:
						
						ack_type = int(data)

						print(f"----> RECIEVING ACK TYPE: {ack_type}")

						# REQUEST FOR COST QUOTE
						if ack_type == ACK.CMD_QUOTE_REQUEST:
							print(f'COST QUOTE REQUESTED')
							# TRACK WHAT THIS WILL DO NEXT
							msg_queue[sock] = ack_type
							# PREPARE IT FOR WRITING
							output.append(sock)
						
						# REQUEST TO RUN COMMAND
						if ack_type == ACK.CMD_EXECUTE:
							print(f'REQUEST TO EXECUTE...')
							msg_queue[sock] = ACK.CMD_EXECUTE
							output.append(sock)

					# INTERPRET EMPTY RESULT AS CLOSED CONNECTION
					else:
						print(f'Closing connections')
						if sock in output:
							output.remove(sock)
						connection_list.remove(sock)
						sock.close()

			for sock in write_sockets:
				if sock:
					print("Entered write")
					# REMOVE CURRENT SOCKET FROM WRITING LIST
					if sock in output:
						output.remove(sock)

					msg_type = msg_queue[sock]
					print(f"WRITING TYPE: {msg_type}")

					# SLEEP
					# rand = random.randint(1, 10)
					# timer = os.getpid() % rand + 2
					# print( f'sleep for: {timer}' )
					# time.sleep(timer)

					# SEND ACK, THAT AFTER THIS I WILL SEND QUOTE
					if msg_type == ACK.CMD_QUOTE_REQUEST:
						send_ack(sock, ACK.CMD_QUOTE_REPLY)
						msg_queue[sock] = ACK.CMD_QUOTE_REPLY
						output.append(sock)

					if msg_type == ACK.CMD_QUOTE_REPLY:
						send_quote(sock)
						del msg_queue[sock]
					
					if msg_type == ACK.CMD_RETURN_STATUS:
						sock.send(str(return_code).encode(FORMAT))
						print(f'Sent return status...')
						del msg_queue[sock]

					if msg_type == ACK.CMD_EXECUTE:
						send_ack(sock, ACK.CMD_ACK)
						msg_queue[sock] = ACK.CMD_EXECUTE
						connection_list.append(sock)


		except KeyboardInterrupt:
			print('Interrupted.')
			# Make sure we close sockets gracefully
			close_sockets(connection_list)
			break


def close_sockets(sockets):
	for sock in sockets:
		sock.close()


def main(port):
	#blocking_socket(SERVER_HOST, int(port))
	non_blocking_socket(SERVER_HOST, int(port))


if __name__ == "__main__":

	if (len(sys.argv) == 1 or sys.argv[1].lower() == 'usage'):
		usage()
	else:
		main(sys.argv[1])