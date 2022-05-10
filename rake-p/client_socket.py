#!/usr/bin/env python3

import socket
import select
import sys

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
		print( f"Socket succesfully created! ({host}:{port})" )

	except socket.error as err:
		print( f'socket creation failed with error {err}' )
	
	print( f'connecting to {host}:{port}...' )
	sd.connect( (host, port) )

	return sd


def send_data(sd, data):
	print( f'sending...' )
	sd.send(data.encode( FORMAT ))


def client_socket(host, port):

	socket_list = []
	write_list  = []

	# ADD ACTIVE SOCKETS
	for p in port:
		socket_list.append(create_socket(host, p))

	# ADD SOCKETS THAT NEED TO SEND DATA
	for p in socket_list:
		write_list.append(p)

	while True:
		try:
			# GET THE LIST OF READABLE SOCKETS
			read_sockets, write_sockets, error_sockets = select.select(socket_list, write_list, [])

			# CHECK IF SOCKETS ARE RECEIVING DATA
			for sock in read_sockets:
				print("entered read sockets")
				if sock:
					print( f'{sock.getsockname()}:receiving...' )
					data_recv = sock.recv( MAX_BYTES ).decode( FORMAT )
					print( f'message: {data_recv}' )
					
					# ADD SOCKET BACK TO WRITE QUEUE
					write_list.append(sock)
			
			# SOCKETS IN write_socket ARE WAITING TO SEND DATA
			for sock in write_sockets:
				print("entered write lists")
				if sock:
					test = f'sending from {sock.getsockname()}'
					print( f"{test}" )

					# SEND DATA
					send_data(sock, test)
					
					# MAKE SURE TO REMOVE SOCKETS FROM write_list ONCE SOCKET HAS SENT DATA
					write_list.remove(sock)

					

		except KeyboardInterrupt:
			print('Interrupted. Closing sockets...')
			# Make sure we close sockets gracefully
			close_sockets(read_sockets)
			close_sockets(write_sockets)
			close_sockets(error_sockets)
			break
		except Exception as err:
			print( f'ERROR occurred in {client_socket.__name__} with code: {err}' )
			break


def close_sockets(sockets):
	for sock in sockets:
		sock.close()


def main(port):
	client_socket(SERVER_HOST, port)


if __name__ == "__main__":

	if (len(sys.argv) == 1 or sys.argv[1].lower() == 'usage'):
		usage()
	else:
		port_list = []

		for port in sys.argv[1:]:
			port_list.append(int(port))
		
		main(port_list)