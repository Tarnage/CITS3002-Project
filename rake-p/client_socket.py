#!/usr/bin/env python3

import socket
import sys
# This shorthand makes one module visible to the other
sys.path.insert(0, '../')
from logger_p import rakelogger

SERVER_PORT = 50009
SERVER_HOST = '192.168.1.105'
MAX_BYTES = 1024
FORMAT = 'utf-8'

# JUST COPYING REFERENCE TO OBJECT FROM rakelogger FOR CONVENIENCE
logger = rakelogger.logger

def usage():
	print("Usage: ")

def client_socket(host, port):
	try:
		sd = socket.socket()
		logger.info("Port succesfully created!")

	except socket.error as err:
		logger.warning( f'socket creation failed with error {err}' )
	
	logger.info( f'connecting to {host}:{port}...' )
	sd.connect( (host, port) )
	logger.info( f'send...' )
	sd.send( "HELLOOO FROM PYTHON CLIENT".encode(FORMAT) )

	logger.info( f'receiving...' )
	data_recv = sd.recv( MAX_BYTES ).decode(FORMAT)
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