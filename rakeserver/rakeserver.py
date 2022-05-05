#!/usr/bin/env python3

import time
import random
import os
import socket
import select
import sys

SERVER_PORT = 50008
# BEAWARE YOU MAY NEED TO EDIT /etc/hosts. TO GET PROPER LOCAL IP ADDRESS
#SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5

ACK_SEND = {
	"CMD_ECHO" 			: 0,
	"CMD_ECHOREPLY" 	: 1,
	"CMD_QUOTE_REQUEST" : 2,
	"CMD_QUOTE_REPLY" 	: 3,
	"CMD_SEND_FILE" 	: 4,
	"CMD_EXECUTE" 		: 5,
	"CMD_RETURN_STATUS" : 6,
	"CMD_RETURN_STDOUT" : 7,
	"CMD_RETURN_STDERR" : 8,
	"CMD_RETURN_FILE" 	: 9
}

ACK_RECV = {
	0 : "CMD_ECHO",
	1 : "CMD_ECHOREPLY",
	2 : "CMD_QUOTE_REQUEST",
	3 : "CMD_QUOTE_REPLY",
	4 : "CMD_SEND_FILE",
	5 : "CMD_EXECUTE",
	6 : "CMD_RETURN_STATUS",
	7 : "CMD_RETURN_STDOUT",
	8 : "CMD_RETURN_STDERR",
	9 : "CMD_RETURN_FILE"
}


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
	sd.send(str(ACK_SEND["CMD_QUOTE_REPLY"]).encode(FORMAT))
	cost = calculate_cost()
	sd.send(str(cost).encode(FORMAT))


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

	connection_list = [sd]
	write_list  = []

	while True:

		try:
			# GET THE LIST OF READABLE SOCKETS
			read_sockets, write_sockets, error_sockets = select.select(connection_list, write_list, [])

			for sock in read_sockets:
				if sock == sd:
					# ESTABLISH CONNECTION WITH CLIENT
					conn, addr = sd.accept()
					print( f'Got a connection from {addr}' )

					# ADD CONECTION TO LIST OF SOCKETS
					connection_list.append(conn)

				else:
					# RECIEVE DATA
					data = sock.recv(MAX_BYTES).decode(FORMAT)
					print( f'Received msg: {data}' )
					
					# REUQEST FOR COST QUOTE
					if int(data) == ACK_SEND["CMD_QUOTE_REQUEST"]:
						send_quote(sock)
						write_list.append(sock)
						connection_list.remove(sock)
					

			for sock in write_sockets:
				if sock:

					# SEND DATA BACK
					send_data = f'Thank you for connecting to {sock.getsockname()}'
					sock.send( send_data.encode(FORMAT) )
					print( f'sending: {send_data}' )

					# ADD SERVER BACK TO LISTENING FOR DATA
					connection_list.append(sd)

					# REMOVE CURRENT SOCKET FROM WRITING LIST
					write_list.remove(sock)

		except KeyboardInterrupt:
			print('Interrupted.')
			# Make sure we close sockets gracefully
			close_sockets(read_sockets)
			close_sockets(write_sockets)
			close_sockets(error_sockets)
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