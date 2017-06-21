# Installation directories.
PREFIX ?= /usr
INCLUDEDIR ?= $(PREFIX)/include
BINDIR ?= $(PREFIX)/bin
LIBDIR ?= $(PREFIX)/lib
MANDIR ?= $(PREFIX)/share/man
LIBSEPOLA ?= $(LIBDIR)/libsepol.a

CFLAGS ?= -Werror -Wall -W

all: semodule_deps

semodule_deps:  semodule_deps.o $(DESTDIR)$(LIBSEPOLA)

install: all
	-mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 semodule_deps $(DESTDIR)$(BINDIR)
	test -d $(DESTDIR)$(MANDIR)/man8 || install -m 755 -d $(DESTDIR)$(MANDIR)/man8
	install -m 644 semodule_deps.8 $(DESTDIR)$(MANDIR)/man8/

relabel:

clean:
	-rm -f semodule_deps *.o

indent:
	../../scripts/Lindent $(wildcard *.[ch])

