# Installation directories.
PREFIX ?= /
SBINDIR ?= $(PREFIX)/usr/sbin
MANDIR = $(PREFIX)/usr/share/man
ETCDIR ?= $(PREFIX)/etc
LIBDIR ?= $(PREFIX)/usr/lib

CFLAGS ?= -Werror -Wall -W
override CFLAGS += -D_FILE_OFFSET_BITS=64
override LDLIBS += -lselinux

all: sestatus

sestatus: sestatus.o

install: all
	[ -d $(DESTDIR)$(MANDIR)/man8 ] || mkdir -p $(DESTDIR)$(MANDIR)/man8
	[ -d $(DESTDIR)$(MANDIR)/man5 ] || mkdir -p $(DESTDIR)$(MANDIR)/man5
	-mkdir -p $(DESTDIR)$(SBINDIR)
	install -m 755 sestatus $(DESTDIR)$(SBINDIR)
	install -m 644 sestatus.8 $(DESTDIR)$(MANDIR)/man8
	install -m 644 sestatus.conf.5 $(DESTDIR)$(MANDIR)/man5
	-mkdir -p $(DESTDIR)$(ETCDIR)
	install -m 644 sestatus.conf $(DESTDIR)$(ETCDIR)

clean:
	rm -f sestatus *.o

indent:
	../../scripts/Lindent $(wildcard *.[ch])

relabel:
