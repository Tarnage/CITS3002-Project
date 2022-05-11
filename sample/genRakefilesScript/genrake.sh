#!/bin/bash

if [ $# == 0 ]
then
	echo "Usage: $0 nfunctions"
	exit 1
fi

# ENSURE THAT THIS REALLY IS A SINGLE tab AND NOT JUST MULTIPLE SPACES
TAB="	"
#
NFILES=$1
PROGRAM="program$NFILES"

# GENERATE ALL THE INDIVIDUAL FUNCTION FILES
echo generating func1.c...func$NFILES.c
for i in $(seq 1 $NFILES)
do
	cat << END_END > func$i.c
int func$i(int x)
{
    return x * x;
}
END_END
done

# GENERATE THE SINGLE Rakefile
echo generating Rakefile$NFILES
cat << END_END > Rakefile$NFILES
PORT  = 12345
HOSTS = localhost

actionset1:
END_END

objs="$PROGRAM.o"
calls="0"
for i in $(seq 1 $NFILES)
do
	echo "${TAB}remote-cc -c func$i.c"
	echo "${TAB}${TAB}requires func$i.c"
	objs="$objs func$i.o"
	calls="$calls + func$i($i)"
done >> Rakefile$NFILES

cat << END_END >> Rakefile$NFILES

actionset2:
${TAB}remote-cc -c $PROGRAM.c
${TAB}${TAB}requires $PROGRAM.c

actionset3:
${TAB}remote-cc -o $PROGRAM $objs
${TAB}${TAB}requires $objs
END_END

# GENERATE THE SINGLE MAIN PROGRAM
echo generating $PROGRAM.c
cat << END_END > $PROGRAM.c
#include <stdio.h>
#include <stdlib.h>

END_END
for i in $(seq 1 $NFILES)
do
    echo "extern int func$i(int i);"
done >> $PROGRAM.c

cat << END_END >> $PROGRAM.c

int main(int argc, char **argv)
{
    printf("%i\n", $calls);
    exit(0);
}
END_END

# LET'S MAKE A Makefile WHILE WE'RE HERE
echo generating Makefile$NFILES
cat << END_END > Makefile$NFILES

$PROGRAM:	$objs
${TAB}cc -o $PROGRAM $objs

$PROGRAM.o:	$PROGRAM.c
${TAB}cc -c $PROGRAM.c

%.o:	%.c
${TAB}cc -c $<

clean:
${TAB}rm -rf $PROGRAM Makefile$NFILES Rakefile$NFILES \
${TAB}$PROGRAM.c func*.c \
${TAB}$objs
END_END

exit 0
