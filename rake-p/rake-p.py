#!/usr/bin/env python3

import parse_rakefile
import client_socket
import sys


def main(argv):
	print(argv)
	parse_rakefile.read_rake(argv[1])

if __name__ == "__main__":
	main(sys.argv)
