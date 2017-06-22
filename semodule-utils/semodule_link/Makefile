# Installation directories.
PREFIX ?= /
INCLUDEDIR ?= $(PREFIX)/usr/include
BINDIR ?= $(PREFIX)/usr/bin
MANDIR ?= $(PREFIX)/usr/share/man
LIBDIR ?= $(PREFIX)/usr/lib

CFLAGS ?= -Werror -Wall -W
override LDLIBS += -lsepol

all: semodule_link

semodule_link:  semodule_link.o 

install: all
	-mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 semodule_link $(DESTDIR)$(BINDIR)
	test -d $(DESTDIR)$(MANDIR)/man8 || install -m 755 -d $(DESTDIR)/$(MANDIR)/man8
	install -m 644 semodule_link.8 $(DESTDIR)$(MANDIR)/man8/

relabel:

clean:
	-rm -f semodule_link *.o

indent:
	../../scripts/Lindent $(wildcard *.[ch])

