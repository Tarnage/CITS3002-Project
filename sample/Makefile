
buildall:	build1 build2 build3
	@make --no-print-directory clean


build1:
	@echo "compile and link all C files at once:"
	cc -o program1 program.c square.c cube.c
	./program1
	@make --no-print-directory clean
	@echo

build2:
	@echo "compile each C file separately, link all object files:"
	cc -c -o program.o program.c
	cc -c -o square.o square.c
	cc -c -o cube.o cube.c
	cc -o program2 program.o square.o cube.o
	./program2
	@make --no-print-directory clean
	@echo

build3:
	@echo "compile each C file separately, link just functions together, link everything:"
	cc -c -o program.o program.c
	cc -c -o square.o square.c
	cc -c -o cube.o cube.c
	ld -r -o allfunctions.o square.o cube.o
	cc -o program3 program.o allfunctions.o
	./program3
	@make --no-print-directory clean
	@echo


clean:
	@rm -f program? *.o
