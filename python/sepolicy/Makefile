PYTHON ?= python

# Installation directories.
PREFIX ?= /usr
LIBDIR ?= $(PREFIX)/lib
BINDIR ?= $(PREFIX)/bin
DATADIR ?= $(PREFIX)/share
MANDIR ?= $(PREFIX)/share/man
LOCALEDIR ?= /usr/share/locale
BASHCOMPLETIONDIR ?= /usr/share/bash-completion/completions
SHAREDIR ?= $(PREFIX)/share/sandbox
CFLAGS ?= -Wall -Werror -Wextra -W
override CFLAGS += -DPACKAGE="policycoreutils" -DSHARED -shared

BASHCOMPLETIONS=sepolicy-bash-completion.sh

all: python-build

python-build:
	$(PYTHON) setup.py build

clean:
	$(PYTHON) setup.py clean
	-rm -rf build *~ \#* *pyc .#*

sepolgen:
	ln -sf sepolicy sepolgen

test:
	@$(PYTHON) test_sepolicy.py -v

install:
	$(PYTHON) setup.py install `test -n "$(DESTDIR)" && echo --root $(DESTDIR)`
	[ -d $(DESTDIR)$(BINDIR) ] || mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 sepolicy.py $(DESTDIR)$(BINDIR)/sepolicy
	(cd $(DESTDIR)$(BINDIR); ln -sf sepolicy sepolgen)
	-mkdir -p $(DESTDIR)$(MANDIR)/man8
	install -m 644 *.8 $(DESTDIR)$(MANDIR)/man8
	-mkdir -p $(DESTDIR)$(BASHCOMPLETIONDIR)
	install -m 644 $(BASHCOMPLETIONS) $(DESTDIR)$(BASHCOMPLETIONDIR)/sepolicy

relabel:
