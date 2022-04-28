import socket
import sys

SERVER_PORT = 50007
SERVER_HOST = ""
MAX_BYTES = 1024

# HOW MANY CONNECTIONS THE SERVER CAN ACCEPT
DEFAULT_BACKLOG = 1

if(len(sys.argv) >= 2 or sys.argv[1].lower() == "usage"):
	print("Usage: ")

else:
	
	try:
		# AF_INET IS THE ADDRESS FAMILY IP4
		# SOCK_STREAM MEANS TCP PROTOCOL IS USED
		sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("Port succesfully created!")
	except socket.error as err:
		print("socket creation failed with error {}".format(err))

	# BIND SOCKET TO PORT
	# TODO: change port if port is used or add try except 
	sd.bind((SERVER_HOST, SERVER_PORT))
	print("Socket is binded to {}".format(SERVER_PORT))

	# PUT THE SOCKET TO LISTEN MODE
	sd.listen(DEFAULT_BACKLOG)
	print("Socket is listening")

	while True:

		# ESTABLISH CONNECTION WITH CLIENT
		conn, addr = sd.accept()
		print("Got a connection from {}".format(addr))

		data = conn.recv(MAX_BYTES).decode()
		print("Received msg: {}".format(data))

		conn.send("Thank you for connecting".encode())

		conn.close()

		break