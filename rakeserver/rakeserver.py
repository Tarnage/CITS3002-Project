#!/usr/bin/env python3

import getopt
import time
import random
import os
import socket
import select
import sys
import subprocess

SERVER_PORT = 50008
# BEAWARE YOU MAY NEED TO EDIT /etc/hosts. TO GET PROPER LOCAL IP ADDRESS
#SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'
# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 5
TIMEOUT 		= 0.5

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
		self.CMD_ACK = 11

# init enum class
ACK = Ack()
return_code = -1


def usage(prog):
	print(f"Usage: {prog} [OPTIONS]...PORT...")
	print("Description")
	print("\tThe purpose of this server program is to receive source files and compile them on the local machine")
	print("Option")
	print("\tIf no options are used, a port number must be given as an argument\n")
	print("\t-h\tdisplay this help and exit\n")
	print("\t-d\twill run default hostname and default port: 50008\n")
	print("\t-v\twill print on delivary of packets\n")
	print("\t-w\twill add a randomised wait timer (0-10secs) between each send request")


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
	print(f'<---- SENDING QUOTE: {cost}')
	sd.send( cost.encode(FORMAT) )


def run_cmd(cmd):
	global return_code

	if not os.path.isdir("./tmp"):
		try:
			os.mkdir("./tmp")
		except OSError as err:
			sys.exit("Directory creation failed with error: {err}")

	print()
	print(f'RUNNING COMMAND: {cmd}')
	p = subprocess.run(cmd, shell=True, cwd='./tmp')
	print(f'COMMAND FINISHED...')
	print()

	return_code = p.returncode


def create_file(filename):
	tmp = "./tmp/"
	if not os.path.exists(filename):
		try:
			with open(tmp + filename, "w") as f:
				pass
		except OSError as err:
			sys.exit(f'File creation failed with error: {err}')


def write_file(filename, data):
	tmp = "./tmp/"
	if not os.path.exists(filename):
		try:
			with open(tmp + filename, "a") as f:
				f.write(data)
		except OSError as err:
			sys.exit(f'File creation failed with error: {err}')


def send_ack(sd, ack_type):
	print(f'<---- SENDING ACK')
	ack = str(ack_type)
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
		# BIND SOCKET TO PORT
		sd.bind( (host, port) )
		print( f'Socket is binded to {port}' )
	except socket.error as err:
		if err.errno == 98:
			sys.exit(f'Binding failed with error: {err}')
		else:
			sys.exit(f'Socket creation failed with error {err}')


	# PUT THE SOCKET TO LISTEN MODE
	sd.listen(DEFAULT_BACKLOG)
	print( f"Socket is listening on {host}..." )
	sd.setblocking(False)

	# SOCKETS WE EXPECT TO READ FROM
	input_sockets = [sd]
	# SOCKETS WE EXPECT TO WRITE TO
	output_sockets  = []
	# OUTGOING MESSAGE QUEUES
	# TRACKS WHAT ACKS SOCKETS ARE WAITING FOR
	msg_queue = {}

	while True:

		try:
			# GET THE LIST OF READABLE SOCKETS
			read_sockets, write_sockets, _ = select.select(input_sockets, output_sockets, [], TIMEOUT)

			for sock in read_sockets:
				print("Reading...")
				if sock == sd:
					# ESTABLISH CONNECTION WITH CLIENT
					conn, addr = sd.accept()
					print( f'Got a connection from {addr}' )

					# ADD CONECTION TO LIST OF SOCKETS
					input_sockets.append(conn)

				else:
					# REMOVE SOCKET FROM INPUT SOCKETS LIST
					# AS WE CONNECT TO IT

					if sock in input_sockets:
						input_sockets.remove(sock)
						
					# RECIEVE DATA
					data = sock.recv(MAX_BYTES).decode(FORMAT)

					# IF THE SOCKET IS IN THE msg_queue THEY ARE WAITING FOR A MESSAGE
					if sock in msg_queue:
						if msg_queue[sock] == ACK.CMD_EXECUTE:
							run_cmd(data)
							msg_queue[sock] = ACK.CMD_RETURN_STATUS
							print(f"after executing sock type: {msg_queue[sock]}")
							output_sockets.append(sock)

					# ELSE THE INITIAL CONNECTION REQUEST 
					elif data:
						
						ack_type = int(data)

						print(f"----> RECIEVING ACK TYPE: {ack_type}")

						# REQUEST FOR COST QUOTE
						if ack_type == ACK.CMD_QUOTE_REQUEST:
							print(f'COST QUOTE REQUESTED')
							# TRACK WHAT THIS WILL DO NEXT
							msg_queue[sock] = ack_type
							# PREPARE IT FOR WRITING
							output_sockets.append(sock)
						
						# REQUEST TO RUN COMMAND
						if ack_type == ACK.CMD_EXECUTE:
							print(f'REQUEST TO EXECUTE...')
							msg_queue[sock] = ACK.CMD_EXECUTE
							output_sockets.append(sock)

					# INTERPRET EMPTY RESULT AS CLOSED CONNECTION
					else:
						print(f'Closing connections')
						if sock in output_sockets:
							output_sockets.remove(sock)
						input_sockets.remove(sock)
						sock.close()

			for sock in write_sockets:
				if sock:
					print("Sending...")
					# REMOVE CURRENT SOCKET FROM WRITING LIST
					if sock in output_sockets:
						output_sockets.remove(sock)

					msg_type = msg_queue[sock]
					print(f"WRITING TYPE: {msg_type}")

					# SLEEP
					# rand = random.randint(1, 10)
					# timer = os.getpid() % rand + 2
					# print( f'sleep for: {timer}' )
					# time.sleep(timer)

					# SEND ACK, THAT AFTER THIS I WILL SEND QUOTE
					if msg_type == ACK.CMD_QUOTE_REQUEST:
						send_ack(sock, ACK.CMD_QUOTE_REPLY)
						msg_queue[sock] = ACK.CMD_QUOTE_REPLY
						output_sockets.append(sock)

					if msg_type == ACK.CMD_QUOTE_REPLY:
						send_quote(sock)
						del msg_queue[sock]
					
					if msg_type == ACK.CMD_RETURN_STATUS:
						sock.send(str(return_code).encode(FORMAT))
						print(f'Sent return status...')
						del msg_queue[sock]

					if msg_type == ACK.CMD_EXECUTE:
						send_ack(sock, ACK.CMD_ACK)
						msg_queue[sock] = ACK.CMD_EXECUTE
						input_sockets.append(sock)

		except KeyboardInterrupt:
			print('Interrupted. Closing sockets...')
			# Make sure we close sockets gracefully
			close_sockets(input_sockets)
			close_sockets(output_sockets)
			sys.exit()


def close_sockets(sockets):
	for sock in sockets:
		sock.close()


def main(port):
	#blocking_socket(SERVER_HOST, int(port))
	non_blocking_socket(SERVER_HOST, int(port))


if __name__ == "__main__":
	# TODO move all this into main
	prog = sys.argv[0][1:]

	if (len(sys.argv) == 2 and sys.argv[1].isnumeric()):
		main(sys.argv[1])
	elif (len(sys.argv) == 1):
		usage(prog)
		sys.exit()
	else:
		try:
			opts, args = getopt.getopt(sys.argv[1:], "hdvw")
			for o, a in opts:
				if o == "-h":
					usage(prog)
					sys.exit()
				elif o == "-v":
					print("TODO verbose")
				elif o == "-d":
					print("TODO default")
				elif o == "-w":
					print("TODO wait")
				else:
					assert False, "unhandled option"

		except getopt.GetoptError as err:
			print(err)
			usage(prog)
		