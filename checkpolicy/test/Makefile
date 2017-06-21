#
# Makefile for building the dispol program
#
PREFIX ?= /usr
BINDIR ?= $(PREFIX)/bin
LIBDIR ?= $(PREFIX)/lib
INCLUDEDIR ?= $(PREFIX)/include
LIBSEPOLA ?= $(LIBDIR)/libsepol.a

CFLAGS ?= -g -Wall -W -Werror -O2 -pipe

all: dispol dismod

dispol: dispol.o $(DESTDIR)$(LIBSEPOLA)

dismod: dismod.o $(DESTDIR)$(LIBSEPOLA)

clean:
	-rm -f dispol dismod *.o 
