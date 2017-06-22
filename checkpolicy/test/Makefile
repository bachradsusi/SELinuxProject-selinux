#
# Makefile for building the dispol program
#
PREFIX ?= /
BINDIR ?= $(PREFIX)/usr/bin
LIBDIR ?= $(PREFIX)/usr/lib
INCLUDEDIR ?= $(PREFIX)/usr/include
LIBSEPOLA ?= $(LIBDIR)/libsepol.a

CFLAGS ?= -g -Wall -W -Werror -O2 -pipe

all: dispol dismod

dispol: dispol.o $(LIBSEPOLA)

dismod: dismod.o $(LIBSEPOLA)

clean:
	-rm -f dispol dismod *.o 
