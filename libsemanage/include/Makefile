# Installation directories.
PREFIX ?= /
INCDIR ?= $(PREFIX)/usr/include/semanage

all:

install: all
	test -d $(DESTDIR)$(INCDIR) || install -m 755 -d $(DESTDIR)$(INCDIR)
	install -m 644 $(wildcard semanage/*.h) $(DESTDIR)$(INCDIR)

indent:
	../../scripts/Lindent $(wildcard semanage/*.h)
