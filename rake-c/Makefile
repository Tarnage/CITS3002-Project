#! /usr/bin/make
UNAME := $(shell uname)

# defining headers
PROJECT = rake-c
HEADERS = $(PROJECT).h
OBJ = parse_c.o rake-c.o strsplit.o
TARGETS = $(basename $(SOURCES))
LIBS =


C11		= cc -std=c11
CFLAGS 	= -Wall -Werror -pedantic

DIRT = $(wildcard *.o) $(PROJECT)

#-----------------------------------------------------------------------------

.PHONY: Makefile

#deafault all: $(TARGETS)

$(PROJECT)	: $(OBJ)
	$(C11) $(CFLAGS) -o $(PROJECT) $(OBJ) $(LIBS)

%.o: %.c $(HEADERS)
	$(C11) $(CFLAGS) -c $<

#-----------------------------------------------------------------------------

clean:
	@echo "Cleaning up...."
	$(RM) $(DIRT)

rmtargets:
	$(RM) $(TARGETS)

clobber: clean rmtargets