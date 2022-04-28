#!/usr/bin/env python3

import socket
import sys
import logging

SERVER_PORT = 50006
SERVER_HOST = ""
MAX_BYTES = 1024

# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 1

def usage():
	print("Usage: ")

def blocking_socket(host, port):
	'''
	Blocking verion of the socket program
	Program will block while waiting for a connection
	'''	
	try:
		# AF_INET IS THE ADDRESS FAMILY IP4
		# SOCK_STREAM MEANS TCP PROTOCOL IS USED
		sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		logging.info("Port succesfully created!")
	except socket.error as err:
		logging.info( f'socket creation failed with error {err}' )

	# BIND SOCKET TO PORT
	# TODO: change port if port is used or add try except 
	sd.bind( (host, port) )
	logging.info( f'Socket is binded to {port}' )

	# PUT THE SOCKET TO LISTEN MODE
	sd.listen(DEFAULT_BACKLOG)
	logging.info("Socket is listening...")

	while True:

		# ESTABLISH CONNECTION WITH CLIENT
		conn, addr = sd.accept()
		logging.info( f'Got a connection from {addr}' )

		data = conn.recv(MAX_BYTES).decode()
		logging.info( f'Received msg: {data}' )

		conn.send( "Thank you for connecting".encode() )

		conn.close()

def non_blocking_socket(host, port):
	'''
	Non Blocking version will contiously poll the socket for connection
	'''

def set_logging(level=logging.INFO):
	logging.basicConfig(filename="./logs/Test.log",\
						level=level,\
						format="%(asctime)s:%(levelname)s:%(message)s",\
						datefmt="%I:%M:%S")

def main():
	set_logging()
	blocking_socket(SERVER_HOST, SERVER_PORT)
	#non_blocking_socket(SERVER_HOST, SERVER_PORT)

if __name__ == "__main__":

	if (len(sys.argv) >= 2):
		usage()
	else:
		main()