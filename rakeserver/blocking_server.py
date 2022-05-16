#!/usr/bin/env python3

import time
import random
import os
import socket
import sys


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
		self.CMD_EXPECT_SOMETHING = 11

ACK = Ack()

SERVER_PORT = 50008
# BEAWARE YOU MAY NEED TO EDIT /etc/hosts. TO GET PROPER LOCAL IP ADDRESS
#SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
TIMEOUT 		= 0.5

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


def main(port):

    blocking_socket(SERVER_HOST, int(port))

if __name__ == "__main__":
    main(sys.argv[1])