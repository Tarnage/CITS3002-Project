        Code 	Meaning
        0 	    No errors or warnings found; object code is generated.
        4 	    Warning: object code is generated and will probably execute correctly.
        8 	    Serious error: object code is generated but may not execute correctly.
        12 	    Serious error: no object code is generated, and pass two of the compiler is not executed.
        16 	    Fatal error: compilation immediately terminates.
        20 	    Fatal error: an abend or internal compiler error occurred. Compilation stops and a dump may be produced.

Geeks for Geeks

        exit(1): It indicates abnormal termination of a program perhaps as a result a minor problem in the code.
        exit(2): It is similar to exit(1) but is displayed when the error occurred is a major one. This statement is rarely seen.
        exit(127): It indicates command not found.
        exit(132): It indicates that a program was aborted (received SIGILL), perhaps as a result of illegal instruction or that the binary is probably corrupt.
        exit(133): It indicates that a program was aborted (received SIGTRAP), perhaps as a result of dividing an integer by zero.
        exit(134): It indicates that a program was aborted (received SIGABRT), perhaps as a result of a failed assertion.
        exit(136): It indicates that a program was aborted (received SIGFPE), perhaps as a result of floating point exception or integer overflow.
        exit(137): It indicates that a program took up too much memory.
        exit(138): It indicates that a program was aborted (received SIGBUS), perhaps as a result of unaligned memory access.
        exit(139): It indicates Segmentation Fault which means that the program was trying to access a memory location not allocated to it. This mostly occurs while using pointers or trying to access an out-of-bounds array index.
        exit(158/152): It indicates that a program was aborted (received SIGXCPU), perhaps as a result of CPU time limit exceeded.
        exit(159/153): It indicates that a program was aborted (received SIGXFSZ), perhaps as a result of File size limit exceeded.