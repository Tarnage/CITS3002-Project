#!/usr/bin/env python3

import socket
import sys
import rakelogger

SERVER_PORT = 50006
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024

# JUST COPYING REFERENCE TO OBJECT FROM rakelogger FOR CONVENIENCE
logger = rakelogger.logger

def usage():
	print("Usage: ")

def client_socket(host, port):
	'''
	Blocking verion of the socket program
	Program will block while waiting for a connection
	'''	
	try:
		sd = socket.socket()
		logger.info("Port succesfully created!")

		sd.connect( (host, port) )
	except socket.error as err:
		logger.info( f'socket creation failed with error {err}' )
	
	logger.info( f'send...' )
	sd.send( "HELLOOO FROM PYTHON CLIENT".encode() )

	logger.info( f'receiving...' )
	data_recv = sd.recv( MAX_BYTES ).decode()
	logger.info( f'message: {data_recv}' )

	sd.close()


def main():
	rakelogger.set_logger()
	client_socket(SERVER_HOST, SERVER_PORT)


if __name__ == "__main__":

	if (len(sys.argv) >= 2):
		usage()
	else:
		main()