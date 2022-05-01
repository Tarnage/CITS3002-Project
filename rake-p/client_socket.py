#!/usr/bin/env python3

import socket
import select
import sys
# This shorthand makes one module visible to the other
sys.path.insert(0, '../')
from logger_p import rakelogger

SERVER_PORT = 50009
#SERVER_HOST = '192.168.1.105'
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'


def usage():
	print("Usage: ")


def create_socket(host, port):
	try:
		sd = socket.socket()
		logger.info( f"Socket succesfully created! ({host}:{port})" )

	except socket.error as err:
		logger.warning( f'socket creation failed with error {err}' )
	
	logger.info( f'connecting to {host}:{port}...' )
	sd.connect( (host, port) )

	logger.info( f'send...' )
	sd.send( "HELLOOO FROM PYTHON CLIENT".encode(FORMAT) )

	return sd


def client_socket(host, port):

	socket_list = []

	for p in port:
		socket_list.append(create_socket(host, p))
	
	while True:
		try:
			# GET THE LIST OF READABLE SOCKETS
			read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

			for sock in read_sockets:
				if sock:
					logger.info( f'receiving...' )
					data_recv = sock.recv( MAX_BYTES ).decode( FORMAT )
					logger.info( f'message: {data_recv}' )

		except KeyboardInterrupt:
			logger.info('Interrupted. Closing sockets...')
			# Make sure we close sockets gracefully
			close_sockets(read_sockets)
			close_sockets(write_sockets)
			close_sockets(error_sockets)
			break
		except Exception as err:
			logger.warning( f'ERROR occurred in {client_socket.__name__} with code: {err}' )
			break


def close_sockets(sockets):
	for sock in sockets:
		sock.close()


def main(port):
	client_socket(SERVER_HOST, port)


if __name__ == "__main__":
	# INIT GLOBAL LOGGER
	global logger
	logger = rakelogger.init_logger()

	if (len(sys.argv) == 1 or sys.argv[1].lower() == 'usage'):
		usage()
	else:
		port_list = []

		for port in sys.argv[1:]:
			port_list.append(int(port))
		
		main(port_list)