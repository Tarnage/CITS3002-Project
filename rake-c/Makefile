
# defining headers
PROJECT = rake-c
HEADERS = $(PROJECT).h
OBJ 	= rake-c.o

C11		= cc -std=c11
CFLAGS 	= -Wall -Werror -pedantic

# headers are accessed by $([headers])
$(PROJECT) : $(OBJ)
	$(C11) $(CFLAGS) -o $(PROJECT) $(OBJ)

%.o : %.c $(HEADERS)
	$(C11) $(CFLAGS) -c $<

# using [make clean] in terminal will remove %.o files
clean :
	rm -f $(PROJECT) $(OBJ)