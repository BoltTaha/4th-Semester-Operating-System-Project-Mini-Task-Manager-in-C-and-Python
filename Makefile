# Makefile

# Variables
CC = gcc
CFLAGS = -Wall
CFILE = task_manager.c
EXEC = task_manager
PYFILE = gui.py

# Default target
all: run_python compile_c run_c

# Compile C program
compile_c:
	$(CC) $(CFLAGS) $(CFILE) -o $(EXEC)

# Run C program
run_c:
	./$(EXEC)

# Run Python program in a new terminal
run_python:
	gnome-terminal -- bash -c "python3 $(PYFILE); exec bash"

# Clean generated files
clean:
	rm -f $(EXEC)

