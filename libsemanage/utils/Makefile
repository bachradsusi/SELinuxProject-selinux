# Installation directories.
PREFIX ?= /
LIBEXECDIR ?= $(PREFIX)/usr/libexec
SELINUXEXECDIR ?= $(LIBEXECDIR)/selinux/

all:

install: all
	-mkdir -p $(DESTDIR)$(SELINUXEXECDIR)
	install -m 755 semanage_migrate_store $(DESTDIR)$(SELINUXEXECDIR)

clean:

distclean: clean

indent:

relabel:

