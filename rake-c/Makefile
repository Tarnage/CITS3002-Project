#! /usr/bin/make

# defining headers
SOURCES = $(wildcard *.c)
HEADERS = $(wildcard *.h)
TARGETS = $(basename $(SOURCES))

C11		= cc -std=c11
CFLAGS 	= -Wall -Werror -pedantic

DIRT = $(wildcard *.o)

#-----------------------------------------------------------------------------

.PHONY: Makefile

deafault all: $(TARGETS)

%: %.c
	$(C11) $(CFLAGS) $^ -o $@

%.i: %.c
	$(C11) -E $(CFLAGS) $< | uniq > $@

#-----------------------------------------------------------------------------

clean:
	@echo "Cleaning up...."
	$(RM) $(DIRT)

rmtargets:
	$(RM) $(TARGETS)

clobber: clean rmtargets