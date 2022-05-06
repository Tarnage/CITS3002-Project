#!/usr/bin/env python3

import time
import random
import os
import socket
import select
import sys
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

ACK_SEND = {
	"CMD_ECHO" 			: 0,
	"CMD_ECHOREPLY" 	: 1,

	"CMD_QUOTE_REQUEST" : 2,
	"CMD_QUOTE_REPLY" 	: 3,

	"CMD_SEND_FILE" 	: 4,

	"CMD_EXECUTE_REQ"	: 5,
	"CMD_EXECUTE" 		: 6,
	"CMD_RETURN_STATUS" : 7,

	"CMD_RETURN_STDOUT" : 8,
	"CMD_RETURN_STDERR" : 9,

	"CMD_RETURN_FILE" 	: 10,
	"CMD_EXPECT_SOMETHING" : 11
}

ACK_RECV = {
	0 : "CMD_ECHO",
	1 : "CMD_ECHOREPLY",

	2 : "CMD_QUOTE_REQUEST",
	3 : "CMD_QUOTE_REPLY",

	4 : "CMD_SEND_FILE",

	5 : "CMD_EXECUTE_REQ",
	6 : "CMD_EXECUTE",
	7 : "CMD_RETURN_STATUS",

	8 : "CMD_RETURN_STDOUT",
	9 : "CMD_RETURN_STDERR",

	10: "CMD_RETURN_FILE",
	11: "CMD_EXPECT_SOMETHING"
}

current_status = 0


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
	print(f'Sending quote: {cost}')
	sd.send( cost.encode(FORMAT) )


def run_cmd(cmd):
	global current_status
	print(cmd)

def send_ack(sd, ack_type):
	if ack_type == ACK_SEND["CMD_QUOTE_REPLY"]:
		print(f'Sending ack: {ACK_RECV[ack_type]}')
		ack = str(ACK_SEND["CMD_QUOTE_REPLY"])
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
	# sd.setblocking(False)
	# SOCKETS WE EXPECT TO READ FROM
	connection_list = [sd]

	# SOCKETS WE EXPECT TO WRITE TO
	output  = []

	# OUTGOING MESSAGE QUEUES
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
					conn.setblocking(False)

					# ADD CONECTION TO LIST OF SOCKETS
					connection_list.append(conn)

				else:
					# RECIEVE DATA
					data = sock.recv(MAX_BYTES).decode(FORMAT)

					print(f'Is sock waiting for a reply {sock in msg_queue}')

					if sock in msg_queue:
						# TODO: not enerting here
						if msg_queue[sock] == ACK_SEND["CMD_EXPECT_SOMETHING"]:
							print(2)
							cmd = data
							run_cmd(cmd)
							msg_queue[sock] == ACK_SEND["CMD_RETURN_STATUS"]
							output.append(sock)
							connection_list.remove(sock)

					elif data:
						
						ack_type = int(data)

						print(f"ENTERED ACK TYPE {ACK_RECV[ack_type]}")

						# REUQEST FOR COST QUOTE
						if ack_type == ACK_SEND["CMD_QUOTE_REQUEST"]:
							print(f'Cost Requested')
							msg_queue[sock] = ack_type
							if sock not in output:
								output.append(sock)
						
						# REQUEST TO RUN COMMAND
						if ack_type == ACK_SEND["CMD_EXECUTE_REQ"]:
							print(1)
							print(f'Request to execute...')
							msg_queue[sock] = ACK_SEND["CMD_EXPECT_SOMETHING"]

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

					# SLEEP
					rand = random.randint(1, 10)
					timer = os.getpid() % rand + 2
					print( f'sleep for: {timer}' )
					time.sleep(timer)
					
					msg_type = msg_queue[sock]

					test_msg_type = ACK_RECV[msg_type]
					print(f"WRITING TYPE: {test_msg_type}")

					# SEND ACK, THAT AFTER THIS I WILL SEND QUOTE
					if msg_type == ACK_SEND["CMD_QUOTE_REQUEST"]:
						send_ack(sock, ACK_SEND["CMD_QUOTE_REPLY"])
						msg_queue[sock] = ACK_SEND["CMD_QUOTE_REPLY"]
						output.append(sock)

					if msg_type == ACK_SEND["CMD_QUOTE_REPLY"]:
						send_quote(sock)
						del msg_queue[sock]
					
					if msg_type == ACK_SEND["CMD_RETURN_STATUS"]:
						print(3)
						sock.send("RETURNED STATUS".encode(FORMAT))
						print(f'Sent return status...')
						del msg_queue[sock]

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