#!/usr/bin/env python3

import sys

class Action:
	def __init__(self, cmd, remote, requires):
		'''
			Args:
				cmd (str): command line to execute
				remote (boolean): run cmd local or remote
				requires (list): list of strings required to execute cmd 
		'''
		self.cmd = cmd
		self.remote = remote
		self.requires = requires

# GLOBAL SO RAKE-P CAN ACCESS 		
default_port = 0

def get_default_port():
	return default_port

def read_rake(filename):
	'''Parse a tab seperated Rakefile

		Args:
		filename (str); filename to be parsed

		Returns:
		host (dict[str]:[int]): key: hostname value: port
		action_sequence( list( list(Action) ) ): will contain action objects to be run in sequence
	'''
	try:
		with open(filename) as rake_file:

			global default_port

			# holds current actionset of Action objects
			# appends the list to action_sequence once all actions in a set is recorded
			action_set = list()

			# track hostname and port number
			hosts = dict()

			# holds all acitionsets to be executed in order
			action_sequence = list()
			
			for line in rake_file:

				# check if line is a comment or empty line
				if not line[0] == '#' and not line == '\n':

					# check if line is for port
					words = line.split()
					if words[0] == 'PORT':
						default_port = int(words[2])
					
					# checks if line is for hosts
					if words[0] == "HOSTS":
						for hostname in words[2:]:
							host_split = hostname.split(":")
							if len(host_split) == 1:
								hosts[host_split[0]] = default_port
							else:
								hosts[host_split[0]] = int(host_split[1])

					# checks single
					if line[0] == '\t' and not line[1] == '\t':

						# split by first occuernace of a '-'
						action_split = line.split('-', 1)
						# if len is > 1 means we have found "remote-"
						if(len(action_split) > 1):
							remote = action_split[0].strip() == "remote"
							action_set.append( Action(action_split[1].strip(), remote, []) )
						else:
							# its a action to be performed locally
							remote = False
							action_set.append( Action(action_split[0].strip(), remote, []) )

					# Checks if double tab
					if line[0] == '\t' and line[1] == '\t':
							last_set = action_set[-1]
							last_set.requires = line.split()
							
					if not line[0] == '\t' and "actionset" in line:
						if len(action_set) > 0:
							action_sequence.append(action_set)
							action_set = list()
			
			# append last action_set tot action_sequence
			action_sequence.append(action_set)

			#print_action_sequence(action_sequence)
			return hosts, action_sequence

	except FileNotFoundError as err:
		print(f"{filename} DOES NOT EXISIT..")
		sys.exit(1)

def print_action_sequence(seq):
	''' for testing
	'''
	counter = 1
	for sequence in seq:
		for actions in sequence:
			print( f'{counter}: remote = {actions.remote}' )
			print( f'cmd = {actions.cmd}' )
			print( f'requires = {actions.requires}' )
			print()
			counter += 1


if __name__ == "__main__":

	read_rake(sys.argv[1])

		