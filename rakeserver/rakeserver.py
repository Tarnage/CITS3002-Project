#!/usr/bin/env python3

import logging
import socket
import sys
import rakelogger

SERVER_PORT = 50006
SERVER_HOST = ""
MAX_BYTES = 1024

# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 1

# JUST COPYING REFERENCE TO OBJECT FROM rakelogger FOR CONVENIENCE
logger = rakelogger.logger

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
		logger.info("Port succesfully created!")
	except socket.error as err:
		logger.info( f'socket creation failed with error {err}' )

	# BIND SOCKET TO PORT
	# TODO: change port if port is used or add try except 
	sd.bind( (host, port) )
	logger.info( f'Socket is binded to {port}' )

	# PUT THE SOCKET TO LISTEN MODE
	sd.listen(DEFAULT_BACKLOG)
	logger.info("Socket is listening...")

	while True:

		# ESTABLISH CONNECTION WITH CLIENT
		conn, addr = sd.accept()
		logger.info( f'Got a connection from {addr}' )

		data = conn.recv(MAX_BYTES).decode()
		logger.info( f'Received msg: {data}' )

		conn.send( "Thank you for connecting".encode() )

		conn.close()


def non_blocking_socket(host, port):
	'''
	Non Blocking version will contiously poll the socket for connection
	'''


def main():
	rakelogger.set_logger()
	blocking_socket(SERVER_HOST, SERVER_PORT)
	#non_blocking_socket(SERVER_HOST, SERVER_PORT)

if __name__ == "__main__":

	if (len(sys.argv) >= 2):
		usage()
	else:
		main()