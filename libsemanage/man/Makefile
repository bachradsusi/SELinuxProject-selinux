# Installation directories.
PREFIX ?= /
MAN3DIR ?= $(PREFIX)/usr/share/man/man3
MAN5DIR ?= $(PREFIX)/usr/share/man/man5

all:

install: all
	mkdir -p $(DESTDIR)$(MAN3DIR)
	mkdir -p $(DESTDIR)$(MAN5DIR)
	install -m 644 man3/*.3 $(DESTDIR)$(MAN3DIR)
	install -m 644 man5/*.5 $(DESTDIR)$(MAN5DIR)

