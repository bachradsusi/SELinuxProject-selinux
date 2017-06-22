# Installation directories.
PREFIX ?= /
MAN5DIR ?= $(PREFIX)/usr/share/man/man5

all:

clean:

install: all
	mkdir -p $(DESTDIR)$(MAN5DIR)
	install -m 644 man5/*.5 $(DESTDIR)$(MAN5DIR)

relabel:
