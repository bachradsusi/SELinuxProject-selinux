# Installation directories.
PREFIX ?= /
BINDIR ?= $(PREFIX)/usr/bin
MANDIR ?= $(PREFIX)/usr/share/man
LOCALEDIR ?= $(PREFIX)/usr/share/locale

.PHONY: all
all: chcat

install: all
	-mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 chcat $(DESTDIR)$(BINDIR)
	-mkdir -p $(DESTDIR)$(MANDIR)/man8
	install -m 644 chcat.8 $(DESTDIR)$(MANDIR)/man8/

clean:

indent:

relabel:
