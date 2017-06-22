# Installation directories.
PREFIX ?= /
LIBDIR ?= $(PREFIX)/usr/lib
SBINDIR ?= $(PREFIX)/usr/sbin
LIBSEPOLA ?= $(LIBDIR)/libsepol.a

CFLAGS ?= -Wall
override CFLAGS += -I../src -D_GNU_SOURCE
override LDLIBS += -lselinux -lpcre

TARGETS=$(patsubst %.c,%,$(sort $(wildcard *.c)))

all: $(TARGETS)

$(TARGETS): ../src/mcstrans.o ../src/mls_level.o $(DESTDIR)$(LIBSEPOLA)

install: all
	-mkdir -p $(DESTDIR)$(SBINDIR)
	install -m 755 $(TARGETS) $(DESTDIR)$(SBINDIR)

test:
	./mlstrans-test-runner.py ../test/*.test

clean:
	rm -f $(TARGETS) *.o *~ \#*

relabel:

