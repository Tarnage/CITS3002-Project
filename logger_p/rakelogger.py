'''
Just a simple logger set-up
usage for logging info in a server-client envionment

NOTE make sure you have a folder named log where you are you using logger, logger can make files but can't make folders.

BEAWARE IF YOU GET AN ERORR ABOUT HOSTNAME YOU MAY NEED TO EDIT '/etc/hosts' FILE
'''

import socket
import logging
from datetime import date

# CREATE LOGGER OBJECT FOR THIS PROGRAM
def init_logger(level=logging.INFO):
	"""Init a logger object
	Creates a logger object and set the name of the logger to
	the hosts name and hosts ip

	Args:
		level (int): set what gets printed to the screen.

	Returns:
		obj: a logger object
	
	"""

	current_date = date.today().strftime("%d-%m-%Y")
	host_name 	= socket.gethostname()
	host_ip 	= socket.gethostbyname(host_name)
	logger 		= logging.getLogger(f'{host_name}-{host_ip}')

	logger.setLevel(logging.DEBUG)

	formatter = logging.Formatter(fmt="%(asctime)s:%(name)s:%(levelname)s:%(message)s", datefmt="%I:%M:%S")
	
	file_handler = logging.FileHandler(filename=f"./logs/{current_date}.log")
	file_handler.setLevel(logging.WARNING)
	file_handler.setFormatter(formatter)
	
	logger.addHandler(file_handler)

	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(level)
	stream_handler.setFormatter(formatter)

	logger.addHandler(stream_handler)

	return logger
