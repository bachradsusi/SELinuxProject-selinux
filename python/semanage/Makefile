PYTHON ?= python

# Installation directories.
PREFIX ?= /usr
LIBDIR ?= $(PREFIX)/lib
SBINDIR ?= $(PREFIX)/sbin
MANDIR = $(PREFIX)/share/man
PYLIBVER ?= $(shell $(PYTHON) -c 'import sys;print("python%d.%d" % sys.version_info[0:2])')
PYTHONLIBDIR ?= $(LIBDIR)/$(PYLIBVER)
BASHCOMPLETIONDIR ?= /usr/share/bash-completion/completions

TARGETS=semanage

BASHCOMPLETIONS=semanage-bash-completion.sh

all: $(TARGETS)

install: all
	[ -d $(DESTDIR)$(MANDIR)/man8 ] || mkdir -p $(DESTDIR)$(MANDIR)/man8
	-mkdir -p $(DESTDIR)$(SBINDIR)
	install -m 755 semanage $(DESTDIR)$(SBINDIR)
	install -m 644 *.8 $(DESTDIR)$(MANDIR)/man8
	test -d $(DESTDIR)$(PYTHONLIBDIR)/site-packages || install -m 755 -d $(DESTDIR)$(PYTHONLIBDIR)/site-packages
	install -m 755 seobject.py $(DESTDIR)$(PYTHONLIBDIR)/site-packages
	-mkdir -p $(DESTDIR)$(BASHCOMPLETIONDIR)
	install -m 644 $(BASHCOMPLETIONS) $(DESTDIR)$(BASHCOMPLETIONDIR)/semanage

test:
	@$(PYTHON) test-semanage.py -a
clean:

indent:

relabel:
