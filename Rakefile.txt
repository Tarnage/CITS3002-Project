# A typical Rakefile

PORT  = 6238
HOSTS = hostname1 hostname2 hostname3:6333

actionset1:
    echo starting actionset1
    remote-cc [optional-flags] -c program.c
        requires program.c program.h allfunctions.h
    remote-cc [optional-flags] -c square.c
        requires square.c allfunctions.h
    remote-cc [optional-flags] -c cube.c
        requires cube.c allfunctions.h

actionset2:
    echo starting actionset2
    remote-cc [optional-flags] -o program program.o square.o cube.o
        requires program.o square.o cube.o