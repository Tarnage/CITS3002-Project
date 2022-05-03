
CC              = cc
CFLAGS          = -std=c99 -O -Wall -Werror -pedantic

OBJ		= strsplit.o

tester:	tester.c $(OBJ)
	$(CC) $(CFLAGS) -o tester tester.c $(OBJ)

%.o:	%.c
	$(CC) $(CFLAGS) -c $<


clean:
	@rm -f tester $(OBJ)
