#!/usr/bin/env python3

from curses.ascii import isdigit
import parse_rakefile
import sys
import socket
import select
import subprocess
import os
import time
import random

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

SERVER_PORT = 50009
#SERVER_HOST = '192.168.1.105'
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'
TIMEOUT 		= 0.5


lowest_host = socket.socket()
lowest_port = 0
lowest_cost = sys.maxsize

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


def send_datagram(sd, ack_type, payload=''):
	if ack_type == ACK_SEND["CMD_QUOTE_REQUEST"]:
		print("Sending cost request...")
		sd.send(str(ack_type).encode(FORMAT))
	
	if ack_type == ACK_SEND["CMD_EXECUTE_REQ"]:
		print(f'sending...')
		sd.send(str(ack_type).encode(FORMAT))

	if ack_type == ACK_SEND["CMD_EXECUTE"]:
		print(f'sending command....')
		sd.send(payload.encode(FORMAT))


def get_lowest_cost(sd, cost):
	global lowest_cost
	global lowest_host
	global lowest_port
	if cost < lowest_cost:
		lowest_cost = int(cost)
		lowest_host, lowest_port = sd.getpeername()


def execute(sd, ack_type, cmd=""):
		# SOCKETS WE EXPECT TO READ FROM
		connection_list = []

		# SOCKETS WE EXPECT TO WRITE TO
		output  = []

		# OUTGOING MESSAGE QUEUES
		msg_queue = {}

		if ack_type == ACK_SEND["CMD_QUOTE_REQUEST"]:
			msg_queue[sd] = ACK_SEND["CMD_QUOTE_REQUEST"]
			output.append(sd)
		
		if ack_type == ACK_SEND["CMD_EXECUTE_REQ"]:
			msg_queue[sd] = ACK_SEND["CMD_EXECUTE_REQ"]
			output.append(sd)
		sd.setblocking(True)

		while True:
			try:
				# GET THE LIST OF READABLE SOCKETS
				read_sockets, write_sockets, error_sockets = select.select(connection_list, output, [], TIMEOUT)

				for sock in read_sockets:
					if sock:
						print(f'Listening for reply')
						# something to read
						data = sock.recv( MAX_BYTES ).decode( FORMAT )
						msg_type = msg_queue[sock]

						if msg_type == ACK_SEND["CMD_QUOTE_REQUEST"]:
							
							if int(data) == ACK_SEND["CMD_QUOTE_REPLY"]:
								msg_queue[sock] = ACK_SEND["CMD_QUOTE_REPLY"]
							else:
								print(f"Recieved the wrong ACK code")


						if msg_type == ACK_SEND["CMD_QUOTE_REPLY"]:
							cost = data
							print(f"Cost: {cost}")
							get_lowest_cost(sock, int(cost))
							connection_list.remove(sock)
							del msg_queue[sock]
							return
						
						if msg_type == ACK_SEND["CMD_RETURN_STATUS"]:
							status = data
							print(f"status code: {status}")
							connection_list.remove(sock)
							del msg_queue[sock]
							return
						
						if msg_type == ACK_SEND["CMD_RETURN_STATUS"]:
							print(f"REVIECD STATUS CODE: {data}")


				for sock in write_sockets:
					if sock:
						if sock in output:
							output.remove(sock)

						# SLEEP
						rand = random.randint(1, 10)
						timer = os.getpid() % rand + 2
						print( f'sleep for: {timer}' )
						time.sleep(timer)

						# something to write
						msg_type = msg_queue[sock]
						print(f"MESSAGE TYPE: {ACK_RECV[msg_type]}")

						if msg_type == ACK_SEND["CMD_QUOTE_REQUEST"]:
							print(f'Sending...')
							send_datagram(sd, msg_type)
							msg_queue[sock] = ACK_SEND["CMD_QUOTE_REQUEST"]
							connection_list.append(sock)
						
						elif msg_type == ACK_SEND["CMD_EXECUTE_REQ"]:
							send_datagram(sd, msg_type)
							msg_queue[sock] = ACK_SEND["CMD_EXECUTE"]
							output.append(sock)
						
						elif msg_type == ACK_SEND["CMD_EXECUTE"]:
							send_datagram(sd, msg_type, cmd)
							msg_queue[sock] = ACK_SEND["CMD_RETURN_STATUS"]
							print("Listening for status")
							connection_list.append(sock)


			except KeyboardInterrupt:
				print('Interrupted. Closing sockets...')
				# Make sure we close sockets gracefully
				# close_sockets(read_sockets)
				# close_sockets(write_sockets)
				# close_sockets(error_sockets)
				break
			#except Exception as err:
			# 	print( f'ERROR occurred in {execute.__name__} with code: {err}' )
			# 	break
	

def get_all_conn(hosts):
	socket_lists = list()
	for key in hosts:
		socket_lists.append(create_socket(key, hosts[key]))
		print(key, hosts[key])
	
	return socket_lists


def main(argv):
	global lowest_host
	global lowest_port

	hosts, actions = parse_rakefile.read_rake(argv[1])

	for sets in actions:
		for command in sets:
			# do we run this command local or remote
			if not command.remote:
				subprocess.run(command.cmd, shell=True)
			# is a remote command
			else:
				# get the lowest cost
				sockets_list = get_all_conn(hosts)
				for sock in sockets_list:
					execute(sock, ACK_SEND["CMD_QUOTE_REQUEST"])
				
				# close_sockets(sockets_list)

				# print(lowest_host, lowest_port)
				slave = create_socket(lowest_host, lowest_port)
				# execute command on the lowest bid
				execute(slave, ACK_SEND["CMD_EXECUTE_REQ"], command.cmd)
			

if __name__ == "__main__":
	main(sys.argv)
