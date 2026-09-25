CC ?= cc
CFLAGS ?= -O0

app: main.o
	$(CC) $(CFLAGS) $^ -o $@

main.o: main.c unused.h
	$(CC) $(CFLAGS) -c main.c -o $@

clean:
	rm -f app main.o
