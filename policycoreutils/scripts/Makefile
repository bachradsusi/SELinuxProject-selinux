# Installation directories.
PREFIX ?= /
SBINDIR ?= $(PREFIX)/sbin
MANDIR ?= $(PREFIX)/usr/share/man
LOCALEDIR ?= $(PREFIX)/usr/share/locale

.PHONY: all
all: fixfiles

install: all
	-mkdir -p $(DESTDIR)$(SBINDIR)
	install -m 755 fixfiles $(DESTDIR)$(SBINDIR)
	-mkdir -p $(DESTDIR)$(MANDIR)/man8
	install -m 644 fixfiles.8 $(DESTDIR)$(MANDIR)/man8/

clean:

indent:

relabel:
