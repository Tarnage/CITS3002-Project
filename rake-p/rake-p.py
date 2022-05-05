#!/usr/bin/env python3

from curses.ascii import isdigit
from unicodedata import digit
import parse_rakefile
import sys
import socket
import select
import subprocess

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


def close_sockets(sockets):
	for sock in sockets:
		sock.close()


def send_request(sd, ack_type):
	if ack_type == ACK_SEND["CMD_QUOTE_REQUEST"]:
		print("Sending cost request... of type {ack_type}")
		sd.send(str(ack_type).encode(FORMAT))
		return sd


def execute(sockets, actions):

	for sets in actions:
		for command in sets:
			# do we run this command local or remote
			if not command.remote:
				subprocess.run(command.cmd, shell=True)
			# is a remote command
			else:
			# broadcast command
				sockets_list = []
				write_list = []
				
				waiting_for_quote = []

				for sd in sockets:
					write_list.append(send_request(sd, ACK_SEND["CMD_QUOTE_REQUEST"]))

				while True:
					try:
						# GET THE LIST OF READABLE SOCKETS
						read_sockets, write_sockets, error_sockets = select.select(sockets, write_list, [])

						# CHECK IF SOCKETS ARE RECEIVING DATA
						for sock in read_sockets:
							print("entered read sockets")
							if sock:
								print( f'{sock.getsockname()}:receiving...' )
								data_recv = sock.recv( MAX_BYTES ).decode( FORMAT )
								print(f"data recieved {data_recv}")
								if data_recv == ACK_SEND["CMD_QUOTE_REPLY"]:
									waiting_for_quote.append(sock)
							
							for waiting in waiting_for_quote:
								if sock == waiting:
									quote = sock.recv( MAX_BYTES ).decode( FORMAT )
									quote = int(quote)
									print(f"Quote recvieved {quote}")


						
						# SOCKETS IN write_socket ARE WAITING TO SEND DATA
						for sock in write_sockets:
							if sock:
								print("entered write lists")
								# MAKE SURE TO REMOVE SOCKETS FROM write_list ONCE SOCKET HAS SENT DATA
								write_list.remove(sock)

					except KeyboardInterrupt:
						print('Interrupted. Closing sockets...')
						# Make sure we close sockets gracefully
						close_sockets(read_sockets)
						close_sockets(write_sockets)
						close_sockets(error_sockets)
						break
					# except Exception as err:
					# 	print( f'ERROR occurred in {execute.__name__} with code: {err}' )
					# 	break
	


def main(argv):
	hosts, actions = parse_rakefile.read_rake(argv[1])

	socket_lists = list()

	for key in hosts:
		socket_lists.append(create_socket(key, hosts[key]))
		print(key, hosts[key])

	execute(socket_lists, actions)
	

if __name__ == "__main__":
	main(sys.argv)
