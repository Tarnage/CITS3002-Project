#! /usr/bin/make

# defining headers
PROJECT = rake-c
HEADERS = $(PROJECT).h
OBJ = client_socket.o parse_c.o rake-c.o strsplit.o execution.c
TARGETS = $(basename $(SOURCES))
LIBS	= logger_c.c

C11		= cc -std=c11
CFLAGS 	= -Wall -Werror -pedantic 

DIRT = $(wildcard *.o)

#-----------------------------------------------------------------------------

.PHONY: Makefile

#deafault all: $(TARGETS)

$(PROJECT)	: $(OBJ)
	$(C11) $(CFLAGS) -o $(PROJECT) $(OBJ)

%.o: %.c $(HEADERS)
	$(C11) $(CFLAGS) -c $<

#-----------------------------------------------------------------------------

clean:
	@echo "Cleaning up...."
	$(RM) $(DIRT)

rmtargets:
	$(RM) $(TARGETS)

clobber: clean rmtargets