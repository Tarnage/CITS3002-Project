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

SERVER_PORT = 50009
#SERVER_HOST = '192.168.1.105'
SERVER_HOST = '127.0.0.1'
MAX_BYTES = 1024
FORMAT = 'utf-8'
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
		self.CMD_EXPECT_SOMETHING = 11

# init enum class
ACK = Ack()

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
	if ack_type == ACK.CMD_QUOTE_REQUEST:
		print("Sending cost request...")
		sd.send(str(ack_type).encode(FORMAT))
	
	if ack_type == ACK.CMD_EXECUTE_REQ:
		print(f'sending...')
		sd.send(str(ack_type).encode(FORMAT))

	if ack_type == ACK.CMD_EXECUTE:
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
		
		if ack_type == ACK.CMD_QUOTE_REQUEST:

			pass
	

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
					execute(sock, ACK.CMD_QUOTE_REQUEST)
				
				# close_sockets(sockets_list)

				# print(lowest_host, lowest_port)
				slave = create_socket(lowest_host, lowest_port)
				# execute command on the lowest bid
				execute(slave, ACK.CMD_EXECUTE, command.cmd)
			

if __name__ == "__main__":
	main(sys.argv)
